import importlib
import importlib.util
import sys
import logging
import re
from typing import Callable, Dict
from types import ModuleType
from pathlib import Path

logger = logging.getLogger(__name__)


class Definition:
    """Loads in a single plugin directory and its submodules for lazy loading."""

    def __init__(self, base_path):
        if base_path[-1] == "/":
            base_path = base_path[:-1]

        self._base_path = base_path
        self.path = Path(base_path)
        self.namespace = base_path.split("/")[-1]
        self.virtualname = None

        self.automations = []

        if not self.path.exists() and not self.path.is_dir():
            raise FileNotFoundError(f"Plugin could not be found at {self._base_path}")

        self._load_plugin()

    def _load_plugin(self):
        """
        Loads a plugin directory and places it in its own namespace so it can be accessed later.
        If `__init__.py` within the plugin defines `__virtualname__`, that will be used as the
        namespace name; otherwise, the plugin directory name is used.

        The plugin can then be accessed under the `plugin` namespace, with submodules lazy-loaded.
        """
        init_file = self.path / "__init__.py"
        if not self.path.is_dir() or not init_file.exists():
            raise FileNotFoundError(
                f"Plugin '{self.namespace}' is missing or lacks an __init__.py file."
            )

        module_import_path = f"{self.namespace}"

        spec = importlib.util.spec_from_file_location(module_import_path, init_file)  # type: ignore
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(module)

            if self.namespace in sys.modules:
                logger.info(f"Reloading plugin '{self.namespace}'")

            sys.modules[self.namespace] = module
            self._load_submodules(self.namespace, self.path)

        else:
            raise ImportError(f"Could not import plugin '{self.namespace}'.")

        return True

    def _load_module_from_file(
        self, name: str, path: Path, namespace: str = ""
    ) -> ModuleType:
        """
        Load a Python module from a file path, ensuring no overwriting occurs.

        If the module is already registered in sys.modules, it reuses the cached instance.
        """
        # Determine fully qualified module name
        module_name = f"{namespace}.{name}" if namespace else name

        # Reuse module if already loaded
        if module_name in sys.modules:
            logger.debug(f"Reusing already loaded module: {module_name}")
            return sys.modules[module_name]

        # Load the module from the file
        spec = importlib.util.spec_from_file_location(module_name, path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load module '{name}' from '{path}'.")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Assign proper name and register in sys.modules
        module.__name__ = module_name
        sys.modules[module_name] = module

        logger.debug(f"Loaded module: {module_name} from {path}")
        return module

    def _load_submodules(
        self,
        namespace: str,
        plugin_path: Path,
        submodule_names: list[str] = SUB_MODULE_NAMES,
    ):
        """
        Load submodules and their files into the provided namespace.

        Prevents overwriting of already loaded modules.
        """
        root_module = sys.modules.get(namespace)
        if not root_module:
            raise ImportError(
                f"Root namespace '{namespace}' is not registered in sys.modules."
            )

        for submodule in submodule_names:
            submodule_path = plugin_path / submodule

            # Handle submodule directories
            if submodule_path.is_dir():
                logger.debug(f"Processing directory submodule: {submodule}")

                # Load __init__.py if present
                init_file = submodule_path / "__init__.py"
                if not init_file.exists():
                    raise ImportError(
                        f"Submodule '{submodule}' is missing __init__.py file."
                    )

                submodule_module = self._load_module_from_file(
                    submodule, init_file, namespace
                )

                # Attach to root module if not already attached
                if not hasattr(root_module, submodule):
                    setattr(root_module, submodule, submodule_module)
                else:
                    logger.debug(
                        f"Submodule '{submodule}' already attached to root module."
                    )

                # Load all .py files in the submodule directory
                for py_file in submodule_path.glob("*.py"):
                    if py_file.name == "__init__.py" or not py_file.is_file():
                        continue

                    file_name = py_file.stem
                    logger.debug(f"Loading file {submodule}/{file_name}")

                    loaded_module = self._load_module_from_file(
                        file_name, py_file, f"{namespace}.{submodule}"
                    )

                    # Attach to submodule if not already attached
                    if not hasattr(submodule_module, file_name):
                        setattr(submodule_module, file_name, loaded_module)
                    else:
                        logger.debug(
                            f"File '{file_name}' already attached to submodule '{submodule}'."
                        )

            # Handle single-file modules
            else:
                logger.debug(f"Processing single-file submodule: {submodule}")
                module_file = plugin_path / f"{submodule}.py"
                if module_file.exists() and module_file.is_file():
                    submodule_module = self._load_module_from_file(
                        submodule, module_file, namespace
                    )

                    # Attach to root module if not already attached
                    if not hasattr(root_module, submodule):
                        setattr(root_module, submodule, submodule_module)
                    else:
                        logger.debug(
                            f"Submodule '{submodule}' already attached to root module."
                        )
                else:
                    logger.warning(
                        f"Submodule '{submodule}' not found at expected path."
                    )

    def get_root(self):
        return sys.modules[self.namespace]

    def _get_name(self, module):
        module_name = module.__name__.split(".")

        if self.virtualname:
            module_name[0] = self.virtualname

        if module_name[-1] not in SUB_MODULE_NAMES:
            if hasattr(module, "__virtualname__"):
                module_name[-1] = getattr(module, "__virtualname__")

        return ".".join(module_name)

    # TODO(Marc) Maybe Cache these results also counts for get_modules
    def get_automations(self) -> Dict[str, Callable]:
        """
        list_automations _summary_

        Returns:
            _description_
        """
        callables = {}

        def get_main_function(module):
            if callable := getattr(module, "main", None):
                return callable

        root_module = getattr(self.get_root(), "automations", None)
        if root_module:
            if callable := get_main_function(root_module):
                callables[self._get_name(root_module)] = callable

            for attr, submodule in root_module.__dict__.items():
                if isinstance(submodule, ModuleType) and not re.compile(
                    r"^__.*__$"
                ).match(attr):
                    if callable := get_main_function(submodule):
                        callables[self._get_name(submodule)] = callable

        return callables

    def get_modules(self) -> Dict[str, Dict[str, Callable]]:
        """
        list_modules
        """
        logger.debug(f"Gathering Modules from {self.namespace}/{self.virtualname}")

        def get_functions(module):
            logger.debug(f"Calling Gathering Functions from {module} using Dir")
            functions = {
                f: getattr(module, f)
                for f in dir(module)
                if callable(getattr(module, f))
            }
            return functions

        modules = getattr(self.get_root(), "modules", None)
        callables = {}
        if modules:
            callables[self._get_name(modules)] = get_functions(modules)
            for attr, submodule in modules.__dict__.items():
                if isinstance(submodule, ModuleType) and not re.compile(
                    r"^__.*__$"
                ).match(attr):
                    logger.debug(f"Checking {attr} for functions")
                    callables[self._get_name(submodule)] = get_functions(submodule)

        return callables

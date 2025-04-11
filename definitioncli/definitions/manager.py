class PluginManager:
    """
    Manages multiple plugins through the lazy plugin loaders
    The plugin manager uses the VirtualName name if defined to access the plugin and its modules
    """

    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, *plugin_dirs):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True  # Mark as initialized to avoid re-initializing

        self.plugins = {}
        for plugin_dir in plugin_dirs:
            try:
                plugin_loader = Plugin(plugin_dir)
                name = plugin_loader.virtualname or plugin_loader.namespace
                self.plugins[name] = plugin_loader
            except Exception as e:
                logger.error(f"Failed to load plugin at {plugin_dir}: {e}")
                continue

    def list_plugins(self) -> list[str]:
        pm = get_plugin_manager()
        return list(pm.plugins.keys())

    def get_plugin(self, name: str = "") -> Optional[Plugin]:
        pm = get_plugin_manager()
        if not name:
            return pm.plugins.get(next(iter(pm.plugins)))
        return pm.plugins.get(name)

    def get_callable(self, path: str) -> Optional[Callable]:
        """
        Returns a callable based on a path string formatted as:
        plugin_name.modules.function_name
        plugin_name.modules.module_name.function_name
        plugin_name.automation.automation_name
        """
        # Get the PluginManager instance
        pm = get_plugin_manager()

        # Split the path and find the plugin
        split_path = path.split(".")
        plugin_name = split_path[0]
        plugin = pm.plugins.get(plugin_name)
        if not plugin:
            return None

        # Resolve the callable based on path structure
        if split_path[1] == "modules":
            return (
                plugin.get_modules()
                .get(".".join(split_path[:-1]), {})
                .get(split_path[-1])
            )
        elif split_path[1] == "automations":
            return plugin.get_automations().get(path)
        else:
            raise ValueError(
                f"Invalid path structure: {path}, expected 'modules' or 'automations'. within second index."
            )


_plugin_manager_instance = None


def setup_plugin_manager(*plugin_dirs: str) -> PluginManager:
    """
    Initializes the PluginManager instance with the specified plugin directories.

    Args:
        plugin_dirs (List[str]): List of directories where plugins are located.

    Returns:
        PluginManager: The initialized PluginManager instance.
    """
    global _plugin_manager_instance
    if _plugin_manager_instance is None:
        if not plugin_dirs:
            raise RuntimeError(
                "plugin_dirs cannot be empty. Provide at least one directory."
            )
        _plugin_manager_instance = PluginManager(*plugin_dirs)

    return _plugin_manager_instance


def teardown_plugin_manager():
    global _plugin_manager_instance
    _plugin_manager_instance = None


def get_plugin_manager() -> PluginManager:
    """
    Retrieves the initialized PluginManager instance.

    Raises:
        ValueError: If the PluginManager has not been initialized.

    Returns:
        PluginManager: The initialized PluginManager instance.
    """
    global _plugin_manager_instance
    if _plugin_manager_instance is None:
        raise RuntimeError(
            "Plugin manager has not been initialized yet. Use 'setup_plugin_manager' first."
        )
    return _plugin_manager_instance

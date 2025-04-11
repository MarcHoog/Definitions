from pydantic import BaseModel, Field
from abc import abstractmethod
from definitioncli.utils import to_snake_case
from definitioncli.templates import get_jinja2_env


class TerraformModule(BaseModel):

    @abstractmethod
    def render(self) -> str:
        """
        Render the Terraform module as a string.
        """

        j2_env = get_jinja2_env()
        template = j2_env.get_template("module.tf.j2")
        kwargs = {
            "module_name": to_snake_case(self.__class__.__name__),
            "module_attr": self.model_dump(),
        }
        return template.render(**kwargs)

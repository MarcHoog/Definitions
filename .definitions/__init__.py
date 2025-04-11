from pydantic import Field
from typing import Text, List, Dict
from definitioncli import TerraformModule


class HetznerServerStorageFirewall(TerraformModule):

    source: Text = Field("../../modules/hetzner_server_storage_firewall")
    server_name: Text
    image: Text
    server_type: Text
    location: Text
    ssh_keys: List[Text]
    volume_name: Text
    volume_size: int = 20

    firewall_name: Text
    firewall_description: Text
    firewall_in_protocol: Text
    firewall_in_port: Text
    firewall_in_source_Ips: List[Text]

    @classmethod
    def __options__(cls) -> Dict:
        return {
            "server_type": [
                "cx11",
                "cx21",
                "cx31",
                "cx41",
            ],
            "location": [
                "cxfr",
            ],
        }

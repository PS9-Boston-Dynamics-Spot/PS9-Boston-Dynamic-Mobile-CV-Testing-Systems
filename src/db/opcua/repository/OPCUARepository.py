from db.opcua.reader.OPCUAReader import OPCUAReader
from db.opcua.exceptions.NodeNotFoundError import NodeNotFoundError
from db.opcua.exceptions.ReaderError import ReaderError
from db.opcua.exceptions.OPCUARepositoryError import OPCUARepositoryError
from db.mapping.output.OPCUANodeMapper import OPCUANodeMapper, OPCUADTO

class OPCUARepository:
    def __init__(self):
        self.reader = OPCUAReader()

    def get_node_value_by_id(self, opcua_node_id: str) -> OPCUADTO:
        try:
            value = self.reader.read_node(node_id=opcua_node_id)
            opcua_dto = OPCUANodeMapper.map_image(value=value)
            return opcua_dto
        except NodeNotFoundError as e:
            raise OPCUARepositoryError(exception=e, error_code=1763731210)
        except ReaderError as e:
            raise OPCUARepositoryError(exception=e, error_code=1763731220)
        except Exception as e:
            OPCUARepositoryError(exception=e, error_code=1763731230)

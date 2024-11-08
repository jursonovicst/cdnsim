# from influxdb import InfluxDBClient
#
# from .log import LogMixIn
#
#
# class InfluxlogMixIn(LogMixIn):
#     def __init__(self, host='localhost', port=8086, username='root', password='root', database=None, **kwargs):
#         super().__init__(**kwargs)
#         self.__client = InfluxDBClient(host, port, username, password, database)
#
#     def _info(self, msg: object) -> None:
#         json_body = [
#             {
#                 "measurement": "cpu_load_short",
#                 "tags": {
#                     "host": "server01",
#                     "region": "us-west"
#                 },
#                 "time": "2009-11-10T23:00:00Z",
#                 "fields": {
#                     "value": 0.64
#                 }
#             }
#         ]
#         self.__client.write_points(json_body)

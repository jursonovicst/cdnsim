from cdnsim.content import Obj
from cdnsim.example import Client, Origin

if __name__ == "__main__":
    client = Client(name="client1", lam=1, alpha=1.2, content_base=[Obj(i) for i in range(1000)])
    origin = Origin(name="origin1")
    client.connect_to(origin)

    client.start_all()
    client.join_all()

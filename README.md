# CDNSim

Two frameworks of [nodes](nodes) and [cdnsim](cdnsim), which are built on each other, and provide classes to
simulate CDN environments.  


## [Nodes](nodes)

Framework to provide multiprocessing, messaging and simulation control features.

blablabla...

### log

### gui



## [CDNSim](cdnsim)

A second framework based on nodes to provide the basic functions and features of a CDN simulation.

### arrival

### requests

### cache

### client

### origin


blablabla...

## Examples

### [Simple](simple)

The simplest implementation of a single cache node.

```text
[client] --> [cache] --> [origin]
```

The client requests a uniform profiles of according to a constant arrival processes, the caches are NonCaches, meaning, they do not cache at all (for demonstration purposes), and the origin is a simple origin.


Create the constant arrival process

```python
class Constant(Arrival):
    def __init__(self, rate: float, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate

    def __next__(self) -> int:
        return int(self.__rate)
```
Create an uniform request profile

```python
class Uniform(Requests):
    """
    Implements a Uniform distribution based request profile.
    """

    def __init__(self, cbase: int):
        """
        :param cbase: number of content
        """
        super().__init__(None)
        self._cbase = cbase

    def generate(self, k: int) -> Self:
        return Requests(pd.Series(randint.rvs(1, self._cbase + 1, size=k)).value_counts())
```

Create a non-caching cache

```python
class NonCache(Cache):
    """
    For demonstration purposes, a non caching cache implementation.
    """
    def _process_ingress(self, requests: Requests) -> None:
        # do not cache, simply forward all requests via a round-robin remote selection
        for remote, request in zip(self.remotes, requests / len(self.remotes)):
            self._send(remote, request)
```

Then create the nodes

```python
client = Client(arrival=Constant(rate=50), requests=Uniform(cbase=20))
cache = NonCache()
origin = Origin()
```

Second, establish connections between the nodes

```python
client.connect_to(cache)
cache.connect_to(origin)
```

Third, run simulation
```python
try:
    client.start_all()
    client.join_all()
except KeyboardInterrupt:
    pass
finally:
    client.terminate()
```

fourth, get stats
```python
...
```


### [CDN 101](cdn_101)

Still simple, but more realistic CDN model.

```text
[client1] -┐┌-> [cache1] -┐
           ├┤             ├-> [cache3] --> [origin]
[client2] -┘└-> [cache2] -┘
```

Create a Poisson arrival process

```python
class Poisson(Arrival):
    def __init__(self, lam: float, **kwargs):
        super().__init__(**kwargs)
        if lam <= 1:
            raise ValueError(f"lambda for poisson should be greater or equal to 1, got: {lam}")
        self.__lam = lam
        self.__rng = np.random.default_rng()

    def __next__(self) -> int:
        return int(self.__rng.poisson(self.__lam, 1)[0])
```

Create a Zipf request profile

```python
class Zipf(Requests):
    """
    Implements a Zipf distribution based request profile.
    """

    def __init__(self, cbase: int, a: float):
        """
        :param cbase: number of content
        :param a: zipf distribution parameter
        """
        super().__init__(None)
        self._cbase = cbase
        self._a = a

    def generate(self, k: int) -> Self:
        return Requests(pd.Series(zipfian.rvs(self._a, self._cbase, size=k)).value_counts())
```

Implement an LFU cache

```python
...
```

Then create the nodes
```python
client1 = Client(arrival=Poisson(lam=50), requests=Zipf(cbase=20, a=1.6))
client2 = Client(arrival=Poisson(lam=80), requests=Zipf(cbase=100, a=1.1))
cache1 = PLFUCache(size=10)
cache2 = PLFUCache(size=10)
cache3 = PLFUCache(size=20)
origin = Origin()
```

Second, establish connections

```python
client1.connect_to(cache1)
client1.connect_to(cache2)
client2.connect_to(cache1)
client2.connect_to(cache2)
cache1.connect_to(cache3)
cache2.connect_to(cache3)
cache3.connect_to(origin)
```

third, run simulation
    
```python
try:
    client1.start_all()
    client1.join_all()
except KeyboardInterrupt:
    pass
finally:
    client1.terminate()
```

fourth, get stats

```python
...
```

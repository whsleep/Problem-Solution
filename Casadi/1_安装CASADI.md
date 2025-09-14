# 安装

## CPP

```shell
sudo apt install -y git cmake gcc g++ gfortran pkg-config liblapack-dev pkg-config coinor-libipopt-dev --install-recommends
```

下载安装

```shell
cd casadi
mkdir build
cd build

cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_IPOPT=ON -DWITH_QPOASES=ON -DWITH_LAPACK=ON
make -j4
sudo make install

```

## python 

```python
pip install casadi
```

## 参考

- [CasADi v3.7.1 latest](https://web.casadi.org/get/)
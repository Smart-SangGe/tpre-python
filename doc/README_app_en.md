# APP Doc

## Run docker

```bash
docker run -it -p 8000-8002:8000-8002 -v ~/mimajingsai/src:/app -e HOST_IP=60.204.193.58 git.mamahaha.work/sangge/tpre:base bash  
docker run -it -p 8000-8002:8000-8002 -v ~/mimajingsai/src:/app -e HOST_IP=119.3.125.234 git.mamahaha.work/sangge/tpre:base bash 
docker run -it -p 8000-8002:8000-8002 -v ~/mimajingsai/src:/app -e HOST_IP=124.70.165.73 git.mamahaha.work/sangge/tpre:base bash 
```

```bash
tpre3: docker run -it -p 8000:8000 -p 8001:8001 -p 8002:8002 -v ~/mimajingsai:/app -e HOST_IP=60.204.233.103 git.mamahaha.work/sangge/tpre:base bash
```
## Deploy contract
You should deploy the contract yourself in src/logger.sol using remix or any CLI-tools and replace the contract address in src/node.py with your actual address.

[Deployment document](https://remix-ide.readthedocs.io/zh-cn/latest/create_deploy.html)

## Start application
You should replace the wallet address/privateKey in src/node.py with your own wallet address/privateKey.

```bash
nohup python server.py &
nohup python node.py &
nohup python client.py &
cat nohup.out
```

## Cloud server ip

**tpre1**: 110.41.155.96  
**tpre2**: 110.41.130.197  
**tpre3**: 110.41.21.35  

## Agent re-encryption process

### Client request message

```bash
python client_cli.py 124.70.165.73 name
python client_cli.py 124.70.165.73 environment
```

## Client router

**/receive_messages**  
post method

**/request_message**  
post method

**/receive_request**  
post method

**/recieve_pk**  
post method  

## Central server router

**/server/show_nodes**  
get method  

**/server/get_node**  
get method  

**/server/delete_node**  
get method  

**/server/heartbeat**  
get method  

**/server/send_nodes_list**  
get method  

## Node router

**/user_src**  
post method  

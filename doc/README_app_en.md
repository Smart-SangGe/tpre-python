# APP Doc

## Run docker

```bash
docker run -it -p 8000:8000 -p 8001:8001 -p 8002:8002 -v ~/mimajingsai:/app -e HOST_IP=110.41.130.197 git.mamahaha.work/sangge/tpre:base bash  
```

```bash
tpre3: docker run -it -p 8000:8000 -p 8001:8001 -p 8002:8002 -v ~/mimajingsai:/app -e HOST_IP=60.204.233.103 git.mamahaha.work/sangge/tpre:base bash
```

## Cloud server ip

**tpre1**: 110.41.155.96  
**tpre2**: 110.41.130.197  
**tpre3**: 110.41.21.35  

## Agent re-encryption process

### Client request message

```bash
python client_cli.py 110.41.21.35 aaa
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

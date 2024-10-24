from eth_logger import call_eth_logger

wallet_address = (
    "0xe02666Cb63b3645E7B03C9082a24c4c1D7C9EFf6"  # 修改成要使用的钱包地址/私钥
)
wallet_pk = "ae66ae3711a69079efd3d3e9b55f599ce7514eb29dfe4f9551404d3f361438c6"

call_eth_logger(wallet_address, wallet_pk, "hello World")

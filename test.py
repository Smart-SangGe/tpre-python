from gmssl import * #pylint: disable = e0401 

sm3 = Sm3() #pylint: disable = e0602
sm3.update(b'1456456')
dgst = sm3.digest()
print("sm3('111') : " + dgst.hex())
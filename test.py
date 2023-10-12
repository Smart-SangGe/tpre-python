from gmssl import * #pylint: disable = e0401 

sm3 = Sm3() #pylint: disable = e0602
sm3.update(b'abc')
dgst = sm3.digest()
print("sm3('abc') : " + dgst.hex())
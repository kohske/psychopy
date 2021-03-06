from psychopy import visual

def testLowGamma():
    """setting gamma low (dark screen)"""
    win = visual.Window([600,600], gamma=0.5)#should make the entire screen bright
    for n in range(5):
        win.flip()
    if win.useNativeGamma==True:
        assert False
    #win.close()
def testHighGamma():
    """setting gamma high (bright screen)"""
    win = visual.Window([600,600], gamma=4.0)#should make the entire screen bright
    for n in range(5):
        win.flip()
    if win.useNativeGamma==True:
        assert False
    #win.close()
def testNoGamma():
    """check that no gamma is used if not passed"""
    win = visual.Window([600,600])#should not change gamma
    if win.useNativeGamma!=True:
        assert False
    #win.close()
    """Or if gamma is provided but by a default monitor?"""
    win = visual.Window([600,600], monitor='testMonitor')#should not change gamma
    if win.useNativeGamma!=True:
        assert False
    #win.close()

import mouse as mo
import keyboard as key
import time
import win32api
import pickle
import os
import queue
# 이 파일이 있는 디렉토리의 절대 경로
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
# pickle 파일이 저장되는 장소
MACRO_FOLDER_PATH = CUR_PATH + '\\' + 'macroFile'
# 마우스 버튼에 따른 상태를 Return 하는 함수
def checkMouseState(key):
    val = win32api.GetKeyState(key)
    #btnType = ['left', 'right']
    return 'down' if val < 0 else ''
def inputFunc(string, val = None):
    if val == None:
        try:
            val = int(input(string))
            return val
        except:
            return 0
    else:
        print(string)
        return val
# 메뉴를 만드는 함수 Input Arg를 통해 메뉴선택 없이 매크로 Run 가능
def makeManu(choose=None, MacroFileIdx=None, playtime=None):
    menue = "---------------------\n"
    menue += "record (1) \n"
    menue += "play (2) \n"
    menue += "---------------------\n"
    menue += "\ninput : "
    val = inputFunc(menue, choose)
    if val == 1:
        return [val]
    elif val == 2:
        menue ='------Select------\n'
        dictMacroName = {}
        print('\n\n')
        for idx, f in enumerate(os.listdir(MACRO_FOLDER_PATH)):
            if os.path.isfile(MACRO_FOLDER_PATH + '\\' + f):
                if f.find('.pickle') > 0:
                    dictMacroName[idx] = f
                    menue += '\t' + str(idx) + '. ' + f + '\n'
        menue += '\ninput : '
        opt = inputFunc(menue, MacroFileIdx)
        playcnt = inputFunc("Input Play Time : ", playtime)
        playcnt = playcnt if playcnt > 0 else 1
        try:
            print(MACRO_FOLDER_PATH)
            macroName = MACRO_FOLDER_PATH + '\\' + dictMacroName[opt]
            return [val, macroName, playcnt]
        except:
            return [0]
    else:
        return [0]
# Record 한 매크로 파일에 이름을 부여하는 코드
def makeNewMacroFileName():
    haveInt = []
    for idx, f in enumerate(os.listdir(MACRO_FOLDER_PATH)):
        if os.path.isfile(MACRO_FOLDER_PATH + '\\' + f):
            if (f.find('NewMacroFile') == 0) and (f.find('.pickle') > 0):
                start = len('NewMacroFile')
                end = f.find('.pickle')
                haveInt.append(int(f[start:end]))
    for idx in range(100):
        dupFlag =0
        for i in haveInt:
            if idx == i:
                dupFlag = 1
                break
        if dupFlag == 0:
            return 'NewMacroFile' + str(idx) + '.pickle'
# Record 함수
def record():
    recorded = queue.Queue()
    m_button_state = checkMouseState(0x04)  # middle button down = 0 or 1. Button up = -127 or -128
    macroStart = False
    print('press middle btn to start recording')
    while not macroStart:
        new_m_button_state = checkMouseState(0x04)
        if new_m_button_state != m_button_state:
            m_button_state = new_m_button_state
            if new_m_button_state == '':
                print('Macro Recording ...')
                macroStart = True
    # global mouse 이벤트를 후킹
    mo.hook(recorded.put)
    # global Keyboard 이벤트를 후킹
    keyHooked = key.hook(recorded.put)
    until = False
    while not until:
        new_m_button_state = checkMouseState(0x04)
        if new_m_button_state != m_button_state:
            m_button_state = new_m_button_state
            if new_m_button_state == '':
                print('Macro Recording End')
                until = True
    # 후킹 종료
    mo.unhook(recorded.put)
    key.unhook(keyHooked)
    #return_list = [mo_first_pos] + list(recorded.queue)
    return_list = list(recorded.queue)
    return return_list
# play 함수 speed_factor를 통해 실행 속도 조절 가능
def play(events, speed_factor=1.0, include_clicks=True, include_moves=True, include_wheel=True):
    state = key.stash_state()
    last_time = None
    for event in events:
        if speed_factor > 0 and last_time is not None:
            time.sleep((event.time - last_time) / speed_factor)
        last_time = event.time
        # F12 를 누르면 play중 종료
        val = key.is_pressed('F12')
        if val == True:
            key.restore_modifiers(state)
            return
        if isinstance(event, mo.ButtonEvent) and include_clicks:
            if event.event_type == mo.UP:
                mo._os_mouse.release(event.button)
            else:
                mo._os_mouse.press(event.button)
        elif isinstance(event, mo.MoveEvent) and include_moves:
            mo._os_mouse.move_to(event.x, event.y)
        elif isinstance(event, mo.WheelEvent) and include_wheel:
            mo._os_mouse.wheel(event.delta)
        else:
            valkey = event.name
            key.press(valkey) if event.event_type == key.KEY_DOWN else key.release(valkey)
    key.restore_modifiers(state)
# main 함수
def runRecoderAndPlayer(choose=None, MacroFileIdx=None, playtime=None):
    while True:
        returnFlag = False
        if choose != None:
            returnFlag = True
        val = makeManu(choose, MacroFileIdx, playtime)
        print(val)
        choose = val[0]
        # 키보드, 마우스 동작 녹화 후 Pickle 파일로 저장
        if choose == 1:
            f_name = makeNewMacroFileName()
            path = MACRO_FOLDER_PATH + '\\' + f_name
            event = record()
            with open(path, 'wb') as f:
                pickle.dump(event, f)
        # pickle 파일을 불러와 키보드, 마우스 동작 수행
        elif choose == 2:
            filename = val[1]
            playcnt = val[2]
            with open(filename, 'rb') as f:
                event = pickle.load(f)
            print(f)
            print(event)
            for i in range(playcnt):
                time.sleep(1)
                play(event)
        else:
            return
        if returnFlag:
            return
        choose = None
if __name__ == "__main__":
    runRecoderAndPlayer()
    # Record 되있는 메크로 가 있다면 아래 코드로 메뉴없이 한번만 호출 가능
    #runRecoderAndPlayer(2, 0, 1)
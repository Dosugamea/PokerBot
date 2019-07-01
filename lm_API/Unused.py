class EventType(object):
    message = 0
    follow = 1
    unfollow = 2
    join = 3
    leave = 4
    postback = 5
    bacon = 6
    accountlink = 7
    _VALUES_TO_NAMES = {
        0:"message",
        1:"follow",
        2:"unfollow",
        3:"join",
        4:"leave",
        5:"postback",
        6:"bacon",
        7:"accountlink"
    }
    _NAMES_TO_VALUES = {
        "message": 0,
        "follow": 1,
        "unfollow": 2,
        "join": 3,
        "leave": 4,
        "postback": 5,
        "bacon": 6,
        "accountlink": 7
    }   
class MessageType(object):
    text = 0
    image = 1
    video = 2
    audio = 3
    file = 4
    location = 5
    sticker = 6
    _VALUES_TO_NAMES = {
        0: "text",
        1: "image",
        2: "video",
        3: "audio",
        4: "file",
        5: "location",
        6: "sticker"
    }
    _NAMES_TO_VALUES = {
        "text": 0,
        "image": 1,
        "video": 2,
        "audio": 3,
        "file": 4,
        "location": 5,
        "sticker": 6
    }
class Tools(object):
    # Make log
    def log(self,text):
        print("[{}] {}".format(str(datetime.now()), text))
    # Register a func to Commander / Runner
    def addFunc(self,func,type="Event"):
        self.funcs.append(func)
    # Register funcs in a class to Commander / Runner
    def addClass(self,_class,type="Event"):
        for func in [x[1] for x in inspect.getmembers(_class, predicate=inspect.ismethod)]:
            self.funcs.append(func)
    # Last crazy solution. use only if can't solve by safe way.
    def makeGlobal(self,names):
        for n in names:
            exec("global %s"%(n))
<?php{
// Ported by Maciej Fijalkowski to PHP (BSD license)

// Task IDs
define('I_IDLE', 1);
define('I_WORK', 2);
define('I_HANDLERA', 3);
define('I_HANDLERB', 4);
define('I_DEVA', 5);
define('I_DEVB', 6);

// Packet types
define('K_DEV', 1000);
define('K_WORK', 1001);

// Packet

define('BUFSIZE', 4);

class Packet {
    

    

}
embed_py_meth("Packet", "def append_to(self, lst):\n        self.link = None\n        if lst is None:\n            return self\n        p = lst\n        next = p.link\n        while next is not None:\n            p = next\n            next = p.link\n        p.link = self\n        return lst");
embed_py_meth("Packet", "def __construct(self, l, i, k):\n        self.link = l\n        self.ident = i\n        self.kind = k\n        self.daturm = 0\n        self.data = [0,0,0,0]");

class TaskRec {}

class DeviceTaskRec extends TaskRec {
    
}
embed_py_meth("DeviceTaskRec", "def __construct(self):\n        self.pending = None");

class IdleTaskRec extends TaskRec {
    
}
embed_py_meth("IdleTaskRec", "def __construct(self):\n        self.control = 1\n        self.count = 10000");

class HandlerTaskRec extends TaskRec {
    

    

    
}
embed_py_meth("HandlerTaskRec", "def deviceInAdd(self, p):\n        x = p.append_to(self.device_in)\n        self.device_in = x\n        return x");
embed_py_meth("HandlerTaskRec", "def workInAdd(self, p):\n        x = p.append_to(self.work_in)\n        self.work_in = x\n        return x");
embed_py_meth("HandlerTaskRec", "def __construct(self):\n        self.work_in = None\n        self.device_in = None");

class WorkTaskRec extends TaskRec {
    
}
embed_py_meth("WorkTaskRec", "def __construct(self):\n        self.destination = I_HANDLERA\n        self.count = 0");

class TaskState {
    

    

    
    
    

    
    
    

    

    

    

    
}
embed_py_meth("TaskState", "def isWaitingWithPacket(self):\n        return self.packet_pending and self.task_waiting and not self.task_holding");
embed_py_meth("TaskState", "def isTaskHoldingOrWaiting(self):\n        return self.task_holding or (not self.packet_pending and self.task_waiting)");
embed_py_meth("TaskState", "def isTaskHolding(self):\n        return self.task_holding");
embed_py_meth("TaskState", "def isTaskWaiting(self):\n        return self.task_waiting");
embed_py_meth("TaskState", "def isPacketPending(self):\n        return self.packet_pending");
embed_py_meth("TaskState", "def waitingWithPacket(self):\n        self.packet_pending = True\n        self.task_waiting = True\n        self.task_holding = False\n        return self");
embed_py_meth("TaskState", "def running(self):\n        self.packet_pending = False\n        self.task_waiting = False\n        self.task_holding = False\n        return self");
embed_py_meth("TaskState", "def waiting(self):\n        self.packet_pending = False\n        self.task_waiting = True\n        self.task_holding = False\n        return self");
embed_py_meth("TaskState", "def packetPending(self):\n        self.packet_pending = True\n        self.task_waiting = False\n        self.task_holding = False\n        return self");
embed_py_meth("TaskState", "def __construct(self):\n        self.packet_pending = True\n        self.task_waiting = False\n        self.task_holding = False");

define('TASKTABSIZE', 10);

$layout = 0;

embed_py_func_global("def trace(a):\n    global layout\n    layout = layout - 1\n    if layout <= 0:\n        print(\"\\n\")\n        layout = 50\n    print \"%s\" % a");

class TaskWorkArea {
    
        
    
}
embed_py_meth("TaskWorkArea", "def reset(self):\n        self.taskTab = []\n        i = 0\n        while i < TASKTABSIZE:\n            self.taskTab.as_list().append(None)\n            i += 1\n        self.taskList = None\n        self.holdCount = 0\n        self.qpktCount = 0");
embed_py_meth("TaskWorkArea", "def __construct(self):\n        self.reset();\n");

class Task extends TaskState {
    

    

    

    

    

    

    

    
}
embed_py_meth("Task", "def findtcb(self, id):\n        t = taskWorkArea.taskTab[id]\n        if t is None:\n            raise Exception(\"Bad task id\")\n        return t");
embed_py_meth("Task", "def qpkt(self, pkt):\n        t = self.findtcb(pkt.ident)\n        taskWorkArea.qpktCount += 1\n        pkt.link = None\n        pkt.ident = self.ident\n        return t.addPacket(pkt, self)");
embed_py_meth("Task", "def release(self, i):\n        t = self.findtcb(i)\n        t.task_holding = False\n        if t.priority > self.priority:\n            return t\n        else:\n            return self");
embed_py_meth("Task", "def hold(self):\n        taskWorkArea.holdCount += 1\n        self.task_holding = True\n        return self.link");
embed_py_meth("Task", "def waitTask(self):\n        self.task_waiting = True\n        return self");
embed_py_meth("Task", "def runTask(self):\n        if self.isWaitingWithPacket():\n            msg = self.input\n            self.input = msg.link\n            if self.input is None:\n                self.running()\n            else:\n                self.packetPending()\n        else:\n            msg = None\n        return self.fn(msg, self.handle)");
embed_py_meth("Task", "def addPacket(self, p, old):\n        if self.input is None:\n            self.input = p\n            self.packet_pending = True\n            if self.priority > old.priority:\n                return self\n        else:\n            p.append_to(self.input)\n        return old");
embed_py_meth("Task", "def __construct(self, i, p, w, initialState, r):\n        self.link = taskWorkArea.taskList\n        self.ident = i\n        self.priority = p\n        self.input = w\n        \n        self.packet_pending = initialState.isPacketPending()\n        self.task_waiting = initialState.isTaskWaiting()\n        self.task_holding = initialState.isTaskHolding()\n        \n        self.handle = r\n        \n        taskWorkArea.taskList = self\n        taskWorkArea.taskTab[i] = self");

class DeviceTask extends Task {
    
}
embed_py_meth("DeviceTask", "def fn(self, pkt, r):\n        d = r\n        if not isinstance(d, DeviceTaskRec):\n            raise Exception(\"not a DeviceTaskRec\")\n        if not pkt:\n            pkt = d.pending\n            if pkt is None:\n                return self.waitTask()\n            else:\n                d.pending = None\n                return self.qpkt(pkt)\n        else:\n            d.pending = pkt\n            if TRACING:\n                trace(pkt.datum)\n            return self.hold()");

class HandlerTask extends Task {
    
}
embed_py_meth("HandlerTask", "def fn(self, pkt, r):\n        h = r\n        if not isinstance(h, HandlerTaskRec):\n            raise Exception(\"not a HandlerTaskRec\")\n        if pkt is not None:\n            if pkt.kind == K_WORK:\n                h.workInAdd(pkt)\n            else:\n                h.deviceInAdd(pkt)\n        work = h.work_in\n        if work is None:\n            return self.waitTask()\n        count = work.datum\n        if count >= BUFSIZE:\n            h.work_in = work.link\n            return self.qpkt(work)\n        \n        dev = h.device_in\n        if dev is None:\n            return self.waitTask()\n        \n        h.device_in = dev.link\n        dev.datum = work.data[count]\n        work.datum = count + 1\n        return self.qpkt(dev)");

class IdleTask extends Task {
    
}
embed_py_meth("IdleTask", "def fn(self, pkt, r):\n        i = r\n        if not isinstance(i, IdleTaskRec):\n            raise Exception(\"not an IdleTaskRec\")\n        i.count -= 1\n        if i.count == 0:\n            return self.hold()\n        elif (i.control & 1) == 0:\n            i.control = i.control / 2\n            return self.release(I_DEVA)\n        else:\n            i.control = (i.control / 2) ^ 53256 # 0xd008\n            return self.release(I_DEVB)");

class WorkTask extends Task {
    
}
embed_py_meth("WorkTask", "def fn(self, pkt, r):\n        w = r\n        if pkt is None:\n            return self.waitTask()\n            \n        if w.destination == I_HANDLERA:\n            dest = I_HANDLERB\n        else:\n            dest = I_HANDLERA\n            \n        w.destination = dest\n        pkt.ident = dest\n        pkt.datum = 0\n        \n        i = 0\n        while i < BUFSIZE:\n            w.count += 1\n            if w.count > 26:\n                w.count = 1\n            temp = ord(\"A\") + w.count - 1\n            pkt.data[i] = ord(\"A\") + w.count - 1\n            i += 1\n            \n        return self.qpkt(pkt)");

define('TRACING', 0);

embed_py_func_global("def schedule():\n    t = taskWorkArea.taskList\n    while t is not None:\n        pkt = None\n        if TRACING:\n            print \"tcp = %d\" % (t.indent)\n        if t.isTaskHoldingOrWaiting():\n            t = t.link\n        else:\n            if TRACING:\n                trace(chr(ord(\"0\") + t.indent))\n            t = t.runTask()");
            
class Richards {

    
}
embed_py_meth("Richards", "def run(self, iterations):\n        i = 0\n        while i < iterations:\n            taskWorkArea.reset()\n            \n            task_state = TaskState()\n            IdleTask(I_IDLE, 1, 10000, task_state.running(), IdleTaskRec())\n            \n            wkq = Packet(None, 0, K_WORK)\n            wkq = Packet(wkq, 0, K_WORK)\n            task_state = TaskState()\n            WorkTask(I_WORK, 1000, wkq, task_state.waitingWithPacket(), WorkTaskRec())\n            \n            wkq = Packet(None, I_DEVA, K_DEV)\n            wkq = Packet(wkq, I_DEVA, K_DEV)\n            wkq = Packet(wkq, I_DEVA, K_DEV)\n            task_state = TaskState()\n            HandlerTask(I_HANDLERA, 2000, wkq, task_state.waitingWithPacket(), HandlerTaskRec())\n            \n            wkq = Packet(None, I_DEVB, K_DEV)\n            wkq = Packet(wkq, I_DEVB, K_DEV)\n            wkq = Packet(wkq, I_DEVB, K_DEV)\n            task_state = TaskState()\n            HandlerTask(I_HANDLERB, 3000, wkq, task_state.waitingWithPacket(), HandlerTaskRec())\n            \n            wkq = None\n            \n            task_state = TaskState()\n            DeviceTask(I_DEVA, 4000, wkq, task_state.waiting(), DeviceTaskRec())\n            task_state = TaskState()\n            DeviceTask(I_DEVB, 5000, wkq, task_state.waiting(), DeviceTaskRec())\n            \n            schedule()\n            \n            if not (taskWorkArea.holdCount == 9297 and taskWorkArea.qpktCount == 23246):\n                return False\n            i += 1\n        return True");

$taskWorkArea = NULL;

function run_iter($n) {
    global $taskWorkArea;
    $taskWorkArea = new TaskWorkArea();
    $r = new Richards();
    $res = $r->run($n);
    assert($res);
}
}?>
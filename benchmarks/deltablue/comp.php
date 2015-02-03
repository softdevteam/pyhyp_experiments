<?php{
// Copyright 2008 the V8 project authors. All rights reserved.
// Copyright 1996 John Maloney and Mario Wolczko.

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

// Ported to PHP from Google's Octane v2.0 benchmarking suite for JavaScript.

// This implementation of the DeltaBlue benchmark is derived
// from the Smalltalk implementation by John Maloney and Mario
// Wolczko. Some parts have been translated directly, whereas
// others have been modified more aggresively to make it feel
// more like a JavaScript program.

embed_py_func_global("def dbg_print_py(func, *args):\n    return\n    \n    import sys\n    sys.stdout.write(\"%s: \" % func)\n    for i in args:\n        sys.stdout.write(\"%s \" % i)\n    sys.stdout.write(\"\\n\")");

// Global variable holding the current planner.
$planner = null;

embed_py_func_global("def alert(s):\n    raise Exception(\"Alert called with argument %s\" % s)");

class OrderedCollection {
  private $elms;
  
  
  
  

  
  
  

  
  
  
}
embed_py_meth("OrderedCollection", "def remove(self, elm):\n    dbg_print_py(\"OrderedCollection::remove\")\n    index = 0\n    skipped = 0\n    for i in xrange(0, len(self.elms)):\n        value = self.elms[i]\n        if value != elm:\n            self.elms[index] = value\n            index += 1\n        else:\n            skipped += 1\n            \n    for i in xrange(0, skipped):\n        self.elms.as_list().pop()");
embed_py_meth("OrderedCollection", "def removeFirst(self):\n    dbg_print_py(\"OrderedCollection::removeFirst\")\n    return self.elms.as_list().pop()");
embed_py_meth("OrderedCollection", "def size(self):\n    dbg_print_py(\"OrderedCollection::size\")\n    return len(self.elms)");
embed_py_meth("OrderedCollection", "def at(self, index):\n    dbg_print_py(\"OrderedCollection::at\", index)\n    return self.elms[index]");
embed_py_meth("OrderedCollection", "def add(self, elm):\n    dbg_print_py(\"OrderedCollection::add\")\n    self.elms.as_list().append(elm)");
embed_py_meth("OrderedCollection", "def __construct(self):\n    dbg_print_py(\"OrderedCollection::constructor\")\n    self.elms = []");

class Strength {
  // Strength constants.
  private static $REQUIRED     = null;
  private static $STONG_PREFERRED  = null;
  private static $PREFERRED    = null;
  private static $STRONG_DEFAULT   = null;
  private static $NORMAL       = null;
  private static $WEAK_DEFAULT   = null;
  private static $WEAKEST      = null;




  

  

  

  

  


  private $strengthValue;
  public $name;
  
  









}
embed_py_meth("Strength", "def nextWeaker(self):\n    dbg_print_py(\"Strength::nextWeaker\")\n    sv = self.strengthValue\n    if sv == 0:\n        return Strength.Weakest()\n    elif sv == 1:\n        return Strength.WeakDefault()\n    elif sv == 2:\n        return Strength.Normal()\n    elif sv == 3:\n        return Strength.StrongDefault()\n    elif sv == 4:\n        return Strength.Preferred()\n    elif sv == 5:\n        return Strength.Required()");
embed_py_meth("Strength", "@php_decor(static=True)\ndef strongest(s1, s2):\n    dbg_print_py(\"Strength::strongest\")\n    return s1 if Strength.stronger(s1, s2) else s2");
embed_py_meth("Strength", "@php_decor(static=True)\ndef weakestOf(s1, s2):\n    dbg_print_py(\"Strength::weakestOf\")\n    return s1 if Strength.weaker(s1, s2) else s2\n");
embed_py_meth("Strength", "@php_decor(static=True)\ndef weaker(s1, s2):\n    dbg_print_py(\"Strength::weaker\")\n    return s1.strengthValue > s2.strengthValue");
embed_py_meth("Strength", "@php_decor(static=True)\ndef stronger(s1, s2):\n    dbg_print_py(\"Strength::stronger\")\n    return s1.strengthValue < s2.strengthValue");
embed_py_meth("Strength", "def __construct(self, strengthValue, name):\n    dbg_print_py(\"Strength::constructor\", strengthValue, name)\n    self.strengthValue = strengthValue\n    self.name = name");
embed_py_meth("Strength", "@php_decor(static=True)\ndef Weakest():\n    dbg_print_py(\"Strength::Weakest\")\n    if not Strength.WEAKEST:\n        Strength.WEAKEST = Strength(6, \"weakest\")\n    return Strength.WEAKEST");
embed_py_meth("Strength", "@php_decor(static=True)\ndef WeakDefault():\n    dbg_print_py(\"Strength::WeakDefault\")\n    if not Strength.WEAK_DEFAULT:\n        Strength.WEAK_DEFAULT = Strength(5, \"weakDefault\")\n    return Strength.WEAK_DEFAULT");
embed_py_meth("Strength", "@php_decor(static=True)\ndef Normal():\n    dbg_print_py(\"Strength::Normal\")\n    if not Strength.NORMAL:\n        Strength.NORMAL = Strength(4, \"normal\")\n    return Strength.NORMAL");
embed_py_meth("Strength", "@php_decor(static=True)\ndef StrongDefault():\n    dbg_print_py(\"Strength::StrongDefault\")\n    if not Strength.STRONG_DEFAULT:\n        Strength.STRONG_DEFAULT = Strength(3, \"strongDefault\")\n    return Strength.STRONG_DEFAULT");
embed_py_meth("Strength", "@php_decor(static=True)\ndef Preferred():\n    dbg_print_py(\"Strength::Preferred\")\n    if not Strength.PREFERRED:\n        Strength.PREFERRED = Strength(2, \"preferred\")\n    return Strength.PREFERRED;");
embed_py_meth("Strength", "@php_decor(static=True)\ndef StrongPreferred():\n    dbg_print_py(\"Strength::Required\")\n    if not Strength.STRONG_PREFERRED:\n        Strength.STRONG_PREFERRED = Strength(1, \"strongPreferred\")\n    return Strength.STRONG_PREFERRED;");
embed_py_meth("Strength", "@php_decor(static=True)\ndef Required():\n  dbg_print_py(\"Strength::Required\")\n  if not Strength.REQUIRED:\n    Strength.REQUIRED = Strength(0, \"required\");\n  return Strength.REQUIRED");


class Constraint {
  public $strength;

  
  
  



  
  
  
}
embed_py_meth("Constraint", "def isInput(self):\n    dbg_print_py(\"Constraint::isInput\")\n    return False");
embed_py_meth("Constraint", "def destroyConstraint(self):\n    dbg_print_py(\"Constraint::destroyConstraint\")\n    if self.isSatisfied():\n        planner.incrementalRemove(self)\n    else:\n        self.removeFromGraph()");
embed_py_meth("Constraint", "def satisfy(self, mark):\n    dbg_print_py(\"Constraint::satisfy\", mark)\n    self.chooseMethod(mark)\n    if not self.isSatisfied():\n        if self.strength == Strength.Required():\n            alert(\"Could not satisfy a required constraint!\")\n        return None\n    self.markInputs(mark)\n    out = self.output()\n    overridden = out.determinedBy\n    if overridden != None:\n        overridden.markUnsatisfied()\n    out.determinedBy = self\n    if not planner.addPropagate(self, mark):\n        alert(\"Cycle encountered\")\n    out.mark = mark\n    return overridden");
embed_py_meth("Constraint", "def addConstraint(self):\n    dbg_print_py(\"Constraint::addConstraint\")\n    self.addToGraph()\n    planner.incrementalAdd(self)\n");
embed_py_meth("Constraint", "def __construct(self, strength):\n    dbg_print_py(\"Constraint::constructor\")\n    self.strength = strength");




class UnaryConstraint extends Constraint {
  public $myOutput;
  public $satisfied;
  
  
  
  


  
  

  

  

  

  

  

    

}
embed_py_meth("UnaryConstraint", "def removeFromGraph(self):\n    dbg_print_py(\"UnaryConstraint::removeFromGraph\")\n    if self.myOutput is not None:\n        self.myOutput.removeConstraint(self)\n    self.satisfied = False");
embed_py_meth("UnaryConstraint", "def inputsKnown(self, *args):\n    dbg_print_py(\"UnaryConstraint::inputsKnown\")\n    return True");
embed_py_meth("UnaryConstraint", "def markUnsatisfied(self):\n    dbg_print_py(\"UnaryConstraint::markUnsatisfied\")\n    self.satisfied = False");
embed_py_meth("UnaryConstraint", "def recalculate(self):\n    dbg_print_py(\"UnaryConstraint::recalculate\")\n    self.myOutput.walkStrength = self.strength\n    self.myOutput.stay = not self.isInput()\n    if self.myOutput.stay:\n        self.execute() # Stay optimisation");
embed_py_meth("UnaryConstraint", "def output(self):\n    dbg_print_py(\"UnaryConstraint::output\")\n    return self.myOutput");
embed_py_meth("UnaryConstraint", "def markInputs(self, mark):\n    dbg_print_py(\"UnaryConstraint::markInputs\", mark)\n    pass");
embed_py_meth("UnaryConstraint", "def isSatisfied(self):\n    dbg_print_py(\"UnaryConstraint::isSatisfied\")\n    return self.satisfied");
embed_py_meth("UnaryConstraint", "def chooseMethod(self, mark):\n    dbg_print_py(\"UnaryConstraint::chooseMethod\", mark)\n    self.satisfied = (self.myOutput.mark != mark) and Strength.stronger(self.strength, self.myOutput.walkStrength)");
embed_py_meth("UnaryConstraint", "def addToGraph(self):\n    dbg_print_py(\"UnaryConstraint::addToGraph\")\n    self.myOutput.addConstraint(self)\n    self.satisfied = False");
embed_py_meth("UnaryConstraint", "def __construct(self, v, strength):\n    dbg_print_py(\"UnaryConstraint::constructor\")\n    Constraint.__construct(self, strength)\n    self.myOutput = v\n    self.satisfied = False\n    self.addConstraint()");

class StayConstraint extends UnaryConstraint {
  
  
  
  
}
embed_py_meth("StayConstraint", "def execute(self):\n    dbg_print_py(\"StayConstraint::execute\")\n    pass");
embed_py_meth("StayConstraint", "def __construct(self, v, str):\n    dbg_print_py(\"StayConstraint::constructor\")\n    UnaryConstraint.__construct(self, v, str)");

class EditConstraint extends UnaryConstraint {

  

  

  
}
embed_py_meth("EditConstraint", "def execute(self):\n    dbg_print_py(\"EditConstraint::execute\")\n    pass");
embed_py_meth("EditConstraint", "def isInput(self):\n    dbg_print_py(\"EditConstraint::isInput\")\n    return True");
embed_py_meth("EditConstraint", "def __construct(self, v, str):\n    dbg_print_py(\"EditConstraint::constructor\")\n    UnaryConstraint.__construct(self, v, str)");


abstract class Direction {
  const NONE   = 0;
  const FORWARD  = 1;
  const BACKWARD = -1;
}


class BinaryConstraint extends Constraint {
  public $v1;
  public $v2;
  public $direction;








  





  
  



  


}
embed_py_meth("BinaryConstraint", "def removeFromGraph(self):\n    dbg_print_py(\"BinaryConstraint::removeFromGraph\")\n    if self.v1 is not None:\n        self.v1.removeConstraint(self)\n    if self.v2 is not None:\n        self.v2.removeConstraint(self)\n    self.direction= Direction.NONE");
embed_py_meth("BinaryConstraint", "def inputsKnown(self, mark):\n    dbg_print_py(\"BinaryConstraint::inputsKnown\", mark)\n    i = self.input()\n    return i.mark == mark or i.stay or i.determinedBy == None");
embed_py_meth("BinaryConstraint", "def markUnsatisfied(self):\n    dbg_print_py(\"BinaryConstraint::markUnsatisfied\")\n    self.direction = Direction.NONE");
embed_py_meth("BinaryConstraint", "def recalculate(self):\n    dbg_print_py(\"BinaryConstraint::recalculate\")\n    ihn = self.input()\n    out = self.output()\n    out.walkStrength = Strength.weakestOf(self.strength, ihn.walkStrength)\n    out.stay = ihn.stay\n    if out.stay:\n        self.execute()");
embed_py_meth("BinaryConstraint", "def output(self):\n    dbg_print_py(\"BinaryConstraint::output\")\n    return self.v2 if self.direction == Direction.FORWARD else self.v1");
embed_py_meth("BinaryConstraint", "def input(self):\n    dbg_print_py(\"BinaryConstraint::input\")\n    return self.v1 if self.direction == Direction.FORWARD else self.v2");
embed_py_meth("BinaryConstraint", "def markInputs(self, mark):\n    dbg_print_py(\"BinaryConstraint::markInputs\", mark)\n    self.input().mark = mark");
embed_py_meth("BinaryConstraint", "def isSatisfied(self):\n    dbg_print_py(\"BinaryConstraint::isSatisfied\")\n    return self.direction != Direction.NONE");
embed_py_meth("BinaryConstraint", "def addToGraph(self):\n    dbg_print_py(\"BinaryConstraint::addToGraph\")\n    self.v1.addConstraint(self)\n    self.v2.addConstraint(self)\n    self.direction = Direction.NONE");
embed_py_meth("BinaryConstraint", "def chooseMethod(self, mark):\n    dbg_print_py(\"BinaryConstraint::chooseMethod\", mark)\n    if self.v1.mark == mark:\n        c1 = self.v2.mark != mark and Strength.stronger(self.strength, self.v2.walkStrength)\n        self.direction = Direction.FORWARD if c1 else Direction.NONE\n    \n    if self.v2.mark == mark:\n        c2 = self.v1.mark != mark and Strength.stronger(self.strength, self.v1.walkStrength)\n        self.direction = Direction.BACKWARD if c2 else Direction.NONE\n        \n    if Strength.weaker(self.v1.walkStrength, self.v2.walkStrength):\n        c3 = Strength.stronger(self.strength, self.v1.walkStrength)\n        self.direction = Direction.BACKWARD if c3 else Direction.NONE\n    else:\n        c4 = Strength.stronger(self.strength, self.v2.walkStrength)\n        self.direction = Direction.FORWARD if c4 else Direction.BACKWARD\n");
embed_py_meth("BinaryConstraint", "def __construct(self, var1, var2, strength):\n    dbg_print_py(\"BinaryConstraint::constructor\")\n    Constraint.__construct(self, strength)\n    self.v1 = var1\n    self.v2 = var2\n    self.direction = Direction.NONE\n    self.addConstraint()\n");

class ScaleConstraint extends BinaryConstraint {
  public $direction;
  public $scale;
  public $offset;



  



  




}
embed_py_meth("ScaleConstraint", "def recalculate(self):\n    dbg_print_py(\"ScaleConstraint::recalculate\")\n    ihn = self.input()\n    out = self.output()\n    out.walkStrength = Strength.weakestOf(self.strength, ihn.walkStrength)\n    out.stay = ihn.stay and self.scale.stay and self.offset.stay\n    \n    if out.stay:\n        self.execute()");
embed_py_meth("ScaleConstraint", "def execute(self):\n    dbg_print_py(\"ScaleConstraint::execute\")\n    if self.direction == Direction.FORWARD:\n        self.v2.value = self.v1.value * self.scale.value + self.offset.value\n    else:\n        self.v1.value = (self.v2.value - self.offset.value) / self.scale.value");
embed_py_meth("ScaleConstraint", "def markInputs(self, mark):\n    dbg_print_py(\"ScaleConstraint::markInputs\", mark)\n    BinaryConstraint.markInputs(self, mark)\n    self.scale.mark = mark\n    self.offset.mark = mark");
embed_py_meth("ScaleConstraint", "def removeFromGraph(self):\n    dbg_print_py(\"ScaleConstraint::removeFromGraph\")\n    BinaryConstraint.removeFromGraph(self)\n    if self.scale is not None:\n        self.scale.removeConstraint(self)\n    if self.offset is not None:\n        self.offset.removeConstraint(self)");
embed_py_meth("ScaleConstraint", "def addToGraph(self):\n    dbg_print_py(\"ScaleConstraint::addToGraph\")\n    BinaryConstraint.addToGraph(self)\n    self.scale.addConstraint(self)\n    self.offset.addConstraint(self)");
embed_py_meth("ScaleConstraint", "def __construct(self, src, scale, offset, dest, strength):\n    dbg_print_py(\"ScaleConstraint::constructor\")\n    self.direction = Direction.NONE\n    self.scale = scale\n    self.offset = offset\n    BinaryConstraint.__construct(self, src, dest, strength)");

class EqualityConstraint extends BinaryConstraint {



  

}
embed_py_meth("EqualityConstraint", "def execute(self):\n    dbg_print_py(\"EqualityConstraint::execute\")\n    self.output().value = self.input().value");
embed_py_meth("EqualityConstraint", "def __construct(self, v1, v2, strength):\n    dbg_print_py(\"EqualityConstraint::constructor\")\n    BinaryConstraint.__construct(self, v1, v2, strength)");

class Variable {
  public $value;
  public $constraints;
  public $determinedBy;
  public $mark;
  public $walkStrength;
  public $stay;
  public $name;


  
  

    

}
embed_py_meth("Variable", "def removeConstraint(self, c):\n    dbg_print_py(\"Variable::removeConstraint\")\n    self.constraints.remove(c)\n    if self.determinedBy == c:\n        self.determinedBy = None");
embed_py_meth("Variable", "def addConstraint(self, c):\n    dbg_print_py(\"Variable::addConstraint\")\n    self.constraints.add(c)");
embed_py_meth("Variable", "def __construct(self, name, initialValue=None):\n    dbg_print_py(\"Variable::constructor\", name)\n    self.value = 0 if initialValue is None else initialValue\n    self.constraints = OrderedCollection()\n    self.determinedBy = None\n    self.mark = 0\n    self.walkStrength = Strength.Weakest()\n    self.stay = True\n    self.name = name");

class Planner {
  
  
  
  



  
  
  
  
  

  


  
  

}
embed_py_meth("Planner", "def addConstraintsConsumingTo(self, v, coll):\n    dbg_print_py(\"Planner::addConstraintsConsumingTo\")\n    determining = v.determinedBy\n    cc = v.constraints\n    i = 0\n    #for i in xrange(0, cc.size()):\n    while i < cc.size():\n        c = cc.at(i)\n        if c != determining and c.isSatisfied():\n            coll.add(c)\n        i += 1");
embed_py_meth("Planner", "def removePropagateFrom(self, out):\n    dbg_print_py(\"Planner::removePropagateFrom\")\n    out.determinedBy = None\n    out.walkStrength = Strength.Weakest()\n    out.stay = True\n    unsatisfied = OrderedCollection()\n    todo = OrderedCollection();\n    todo.add(out)\n    while todo.size() > 0:\n        v = todo.removeFirst()\n        #for i in xrange(v.constraints.size()):\n        i = 0\n        while i < v.constraints.size():\n            c = v.constraints.at(i)\n            if not c.isSatisfied():\n                unsatisfied.add(c)\n            i += 1\n        determining = v.determinedBy\n        #for i in xrange(v.constraints.size()):\n        i = 0\n        while i < v.constraints.size():\n            next = v.constraints.at(i)\n            if next != determining and next.isSatisfied():\n                next.recalculate()\n                todo.add(next.output())\n            i += 1\n    return unsatisfied\n");
embed_py_meth("Planner", "def addPropagate(self, c, mark):\n    dbg_print_py(\"Planner::addPropagate\", mark)\n    todo = OrderedCollection()\n    todo.add(c)\n    while todo.size() > 0:\n        d = todo.removeFirst()\n        if d.output().mark == mark:\n            self.incrementalRemove(c)\n            return False\n        d.recalculate()\n        self.addConstraintsConsumingTo(d.output(), todo)\n    return True");
embed_py_meth("Planner", "def extractPlanFromConstraints(self, constraints):\n    dbg_print_py(\"Planner::extractPlanFromConstraints\")\n    sources = OrderedCollection()\n    #for i in xrange(0, constraints.size()):\n    i = 0\n    while i < constraints.size():\n        c = constraints.at(i)\n        # not in plan already and eligible for inclusion\n        if c.isInput() and c.isSatisfied():\n            sources.add(c)\n        i += 1\n    return self.makePlan(sources)");
embed_py_meth("Planner", "def makePlan(self, sources):\n    dbg_print_py(\"Planner::makePlan\")\n    mark = self.newMark()\n    plan = Plan()\n    todo = sources\n    while todo.size() > 0:\n        c = todo.removeFirst()\n        if c.output().mark != mark and c.inputsKnown(mark):\n            plan.addConstraint(c)\n            c.output().mark = mark\n            self.addConstraintsConsumingTo(c.output(), todo)\n    return plan");
embed_py_meth("Planner", "def newMark(self):\n    dbg_print_py(\"Planner::newMark\")\n    self.currentMark += 1\n    return self.currentMark");
embed_py_meth("Planner", "def incrementalRemove(self, c):\n    dbg_print_py(\"Planner::incrementalRemove\")\n    out = c.output()\n    c.markUnsatisfied()\n    c.removeFromGraph()\n    unsatisfied = self.removePropagateFrom(out)\n    strength = Strength.Required()\n    while True:\n        #for i in xrange(unsatisfied.size()):\n        i = 0\n        while i < unsatisfied.size():\n            u = unsatisfied.at(i)\n            if u.strength == strength:\n                self.incrementalAdd(u)\n            i += 1\n        strength = strength.nextWeaker()\n        if strength == Strength.Weakest():\n            break");
embed_py_meth("Planner", "def incrementalAdd(self, c):\n    dbg_print_py(\"Planner::incrementalAdd\")\n    mark = self.newMark()\n    overridden = c.satisfy(mark)\n    while overridden is not None:\n        overridden = overridden.satisfy(mark)");
embed_py_meth("Planner", "def __construct(self):\n    dbg_print_py(\"Planner::constructor\")\n    self.currentMark = 0");

class Plan {
  private $v;

  

  
  
  
  
  
 
    

}
embed_py_meth("Plan", "def execute(self):\n    dbg_print_py(\"Plan::execute\")\n    i = 0\n    #for i in xrange(0, self.size()):\n    while i < self.size():\n        c = self.constraintAt(i)\n        c.execute()\n        i += 1");
embed_py_meth("Plan", "def constraintAt(self, index):\n    dbg_print_py(\"Plan::constraintAt\",index)\n    return self.v.at(index)");
embed_py_meth("Plan", "def size(self):\n    dbg_print_py(\"Plan::size\")\n    return self.v.size()");
embed_py_meth("Plan", "def addConstraint(self, c):\n    dbg_print_py(\"Plan::addConstraint\")\n    self.v.add(c)");
embed_py_meth("Plan", "def __construct(self):\n    dbg_print_py(\"Plan::constructor\")\n    self.v = OrderedCollection()");

// XXX needed becuase there is currently no way to modify a global PHP var from Python
function set_planner($p) {
    global $planner;
    $planner = $p;
}

embed_py_func_global("def chainTest(n):\n    dbg_print_py(\"chainTest\", n)\n    \n    #planner = Planner()\n    set_planner(Planner())\n    prev = first = last = None\n    \n    for i in xrange(n + 1):\n        name = \"v%s\" % i\n        v = Variable(name)\n        if prev is not None:\n            EqualityConstraint(prev, v, Strength.Required())\n        if i == 0:\n            first = v\n        if i == n:\n            last = v\n        prev = v\n    \n    StayConstraint(last, Strength.StrongDefault())\n    edit = EditConstraint(first, Strength.Preferred())\n    edits = OrderedCollection()\n    edits.add(edit)\n    plan = planner.extractPlanFromConstraints(edits)\n    for i in xrange(100):\n        first.value = i\n        plan.execute()\n        if last.value != i:\n            alert(\"Chain test failed\")");


embed_py_func_global("def projectionTest(n):\n    dbg_print_py(\"projectionTest\", n)\n    set_planner(Planner())\n    \n    scale = Variable(\"scale\", 10)\n    offset = Variable(\"offset\", 1000)\n    src = dst = None\n    \n    dests = OrderedCollection()\n    for i in xrange(n):\n        src = Variable(\"src%d\" % i, i)\n        dst = Variable(\"dst%d\" % i, i)\n        dests.add(dst)\n        StayConstraint(src, Strength.Normal())\n        ScaleConstraint(src, scale, offset, dst, Strength.Required())\n        \n    change(src, 17)\n    if dst.value != 1170:\n        alert(\"Projection 1 failed\")\n    change(dst, 1050)\n    if src.value != 5:\n        alert(\"Projection 2 failed\")\n    change(scale, 5)\n    for i in xrange(n - 1):\n        if dests.at(i).value != i * 5 + 1000:\n            alert(\"Projection 3 failed\")\n    change(offset, 2000);\n    for i in xrange(n - 1):\n        if dests.at(i).value != i * 5 + 2000:\n            alert(\"Projection 4 failed\");\n");
            
embed_py_func_global("def change(v, newValue):\n    dbg_print_py(\"change\", newValue)\n    edit = EditConstraint(v, Strength.Preferred())\n    edits = OrderedCollection()\n    edits.add(edit)\n    plan = planner.extractPlanFromConstraints(edits)\n    for i in xrange(10):\n        v.value = newValue\n        plan.execute()\n    edit.destroyConstraint()");

function run_iter($n) {
  chainTest($n);
  projectionTest($n);
}
}?>
# Copyright 2008 the V8 project authors. All rights reserved.
# Copyright 1996 John Maloney and Mario Wolczko.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Ported to PHP from Google's Octane v2.0 benchmarking suite for JavaScript.
#
# This implementation of the DeltaBlue benchmark is derived
# from the Smalltalk implementation by John Maloney and Mario
# Wolczko. Some parts have been translated directly, whereas
# others have been modified more aggresively to make it feel
# more like a JavaScript program.

# Global variable holding the current planner.
planner = None

def alert(s):
    raise Exception("Alert called with argument %s" % s)

class OrderedCollection(object):

  def __init__(self):
    self.elms = []

  def add(self, elm):
    self.elms.append(elm)

  def at(self, index):
    return self.elms[index]

  def size(self):
    return len(self.elms)

  def removeFirst(self):
    return self.elms.pop()

  def remove(self, elm):
    index = 0
    skipped = 0
    for i in xrange(0, len(self.elms)):
      value = self.elms[i]
      if value != elm:
        self.elms[index] = value
        index += 1
      else:
        skipped += 1

    for i in xrange(0, skipped):
      self.elms.pop()

class Strength(object):

  REQUIRED     = None
  STONG_PREFERRED  = None
  PREFERRED    = None
  STRONG_DEFAULT   = None
  NORMAL       = None
  WEAK_DEFAULT   = None
  WEAKEST      = None

  @staticmethod
  def Required():
    if not Strength.REQUIRED:
      Strength.REQUIRED = Strength(0, "required");
    return Strength.REQUIRED

  @staticmethod
  def StrongPreferred():
    if not Strength.STRONG_PREFERRED:
      Strength.STRONG_PREFERRED = Strength(1, "strongPreferred")
    return Strength.STRONG_PREFERRED;

  @staticmethod
  def Preferred():
    if not Strength.PREFERRED:
      Strength.PREFERRED = Strength(2, "preferred")
    return Strength.PREFERRED;

  @staticmethod
  def StrongDefault():
    if not Strength.STRONG_DEFAULT:
      Strength.STRONG_DEFAULT = Strength(3, "strongDefault")
    return Strength.STRONG_DEFAULT

  @staticmethod
  def Normal():
    if not Strength.NORMAL:
      Strength.NORMAL = Strength(4, "normal")
    return Strength.NORMAL

  @staticmethod
  def WeakDefault():
    if not Strength.WEAK_DEFAULT:
      Strength.WEAK_DEFAULT = Strength(5, "weakDefault")
    return Strength.WEAK_DEFAULT

  @staticmethod
  def Weakest():
    if not Strength.WEAKEST:
      Strength.WEAKEST = Strength(6, "weakest")
    return Strength.WEAKEST

  def __init__(self, strengthValue, name):
    self.strengthValue = strengthValue
    self.name = name

  @staticmethod
  def stronger(s1, s2):
    return s1.strengthValue < s2.strengthValue

  @staticmethod
  def weaker(s1, s2):
    return s1.strengthValue > s2.strengthValue

  @staticmethod
  def weakestOf(s1, s2):
    return s1 if Strength.weaker(s1, s2) else s2

  @staticmethod
  def strongest(s1, s2):
    return s1 if Strength.stronger(s1, s2) else s2

  def nextWeaker(self):
    sv = self.strengthValue
    if sv == 0:
      return Strength.Weakest()
    elif sv == 1:
      return Strength.WeakDefault()
    elif sv == 2:
      return Strength.Normal()
    elif sv == 3:
      return Strength.StrongDefault()
    elif sv == 4:
      return Strength.Preferred()
    elif sv == 5:
      return Strength.Required()

class Constraint(object):

  def __init__(self, strength):
    self.strength = strength

  def addConstraint(self):
    self.addToGraph()
    planner.incrementalAdd(self)

  def satisfy(self, mark):
    self.chooseMethod(mark)
    if not self.isSatisfied():
      if self.strength == Strength.Required():
        alert("Could not satisfy a required constraint!")
      return None
    self.markInputs(mark)
    out = self.output()
    overridden = out.determinedBy
    if overridden != None:
      overridden.markUnsatisfied()
    out.determinedBy = self
    if not planner.addPropagate(self, mark):
      alert("Cycle encountered")
    out.mark = mark
    return overridden

  def destroyConstraint(self):
    if self.isSatisfied():
      planner.incrementalRemove(self)
    else:
      self.removeFromGraph()

  def isInput(self):
    return False

class UnaryConstraint(Constraint):

  def __init__(self, v, strength):
    Constraint.__init__(self, strength)
    self.myOutput = v
    self.satisfied = False
    self.addConstraint()

  def addToGraph(self):
    self.myOutput.addConstraint(self)
    self.satisfied = False

  def chooseMethod(self, mark):
    self.satisfied = (self.myOutput.mark != mark) and \
      Strength.stronger(self.strength, self.myOutput.walkStrength)

  def isSatisfied(self):
    return self.satisfied

  def markInputs(self, mark):
    pass

  def output(self):
    return self.myOutput

  def recalculate(self):
    self.myOutput.walkStrength = self.strength
    self.myOutput.stay = not self.isInput()
    if self.myOutput.stay:
      self.execute() # Stay optimisation

  def markUnsatisfied(self):
    self.satisfied = False

  def inputsKnown(self, *args):
    return True

  def removeFromGraph(self):
    if self.myOutput is not None:
      self.myOutput.removeConstraint(self)
    self.satisfied = False

class StayConstraint(UnaryConstraint):

  def __init__(self, v, str):
    UnaryConstraint.__init__(self, v, str)

  def execute(self):
    pass

class EditConstraint(UnaryConstraint):

  def __init__(self, v, str):
    UnaryConstraint.__init__(self, v, str)

  def isInput(self):
    return True

  def execute(self):
    pass


class Direction(object):
  NONE   = 0;
  FORWARD  = 1;
  BACKWARD = -1;

class BinaryConstraint(Constraint):

  def __init__(self, var1, var2, strength):
    Constraint.__init__(self, strength)
    self.v1 = var1
    self.v2 = var2
    self.direction = Direction.NONE
    self.addConstraint()

  def chooseMethod(self, mark):
    if not self.v1.mark == mark:
      c1 = self.v2.mark != mark and \
          Strength.stronger(self.strength, self.v2.walkStrength)
      self.direction = Direction.FORWARD if c1 else Direction.NONE

    if self.v2.mark == mark:
      c2 = self.v1.mark != mark and \
        Strength.stronger(self.strength, self.v1.walkStrength)
      self.direction = Direction.BACKWARD if c2 else Direction.NONE

    if Strength.weaker(self.v1.walkStrength, self.v2.walkStrength):
      c3 = Strength.stronger(self.strength, self.v1.walkStrength)
      self.direction = Direction.BACKWARD if c3 else Direction.NONE
    else:
      c4 = Strength.stronger(self.strength, self.v2.walkStrength)
      self.direction = Direction.FORWARD if c4 else Direction.BACKWARD

  def addToGraph(self):
    self.v1.addConstraint(self)
    self.v2.addConstraint(self)
    self.direction = Direction.NONE

  def isSatisfied(self):
    return self.direction != Direction.NONE

  def markInputs(self, mark):
    self.input().mark = mark

  def input(self):
    return self.v1 if self.direction == Direction.FORWARD else self.v2

  def output(self):
    return self.v2 if self.direction == Direction.FORWARD else self.v1

  def recalculate(self):
    ihn = self.input()
    out = self.output()
    out.walkStrength = Strength.weakestOf(self.strength, ihn.walkStrength)
    out.stay = ihn.stay
    if out.stay:
      self.execute()

  def markUnsatisfied(self):
    self.direction = Direction.NONE

  def inputsKnown(self, mark):
    i = self.input()
    return i.mark == mark or i.stay or i.determinedBy == None

  def removeFromGraph(self):
    if self.v1 is not None:
      self.v1.removeConstraint(self)
    if self.v2 is not None:
      self.v2.removeConstraint(self)
    self.direction= Direction.NONE

  def PYremoveFromGraph(self):
    if self.v1 is not None:
      self.v1.removeConstraint(self)
    if self.v2 is not None:
      self.v2.removeConstraints(self)
    self.direction = Direction.None

class ScaleConstraint(BinaryConstraint):

  def __init__(self, src, scale, offset, dest, strength):
    self.direction = Direction.NONE
    self.scale = scale
    self.offset = offset
    BinaryConstraint.__init__(self, src, dest, strength)

  def addToGraph(self):
    BinaryConstraint.addToGraph(self)
    self.scale.addConstraint(self)
    self.offset.addConstraint(self)

  def removeFromGraph(self):
    BinaryConstraint.removeFromGraph(self)
    if self.scale is not None:
        self.scale.removeConstraint(self)
    if self.offset is not None:
        self.offset.removeConstraint(self)

  def markInputs(self, mark):
    BinaryConstraint.markInputs(self, mark)
    self.scale.mark = mark
    self.offset.mark = mark

  def execute(self):
    if self.direction == Direction.FORWARD:
      self.v2.value = self.v1.value * self.scale.value + self.offset.value
    else:
      self.v1.value = (self.v2.value - self.offset.value) / self.scale.value

  def recalculate(self):
    ihn = self.input()
    out = self.output()
    out.walkStrength = Strength.weakestOf(self.strength, ihn.walkStrength)
    out.stay = ihn.stay and self.scale.stay and self.offset.stay

    if out.stay:
      self.execute()

class EqualityConstraint(BinaryConstraint):

  def __init__(self, v1, v2, strength):
    BinaryConstraint.__init__(self, v1, v2, strength)

  def execute(self):
    self.output().value = self.input().value


class Variable(object):

  def __init__(self, name, initialValue=None):
    self.value = 0 if initialValue is None else initialValue
    self.constraints = OrderedCollection()
    self.determinedBy = None
    self.mark = 0
    self.walkStrength = Strength.Weakest()
    self.stay = True
    self.name = name

  def addConstraint(self, c):
    self.constraints.add(c)

  def removeConstraint(self, c):
    self.constraints.remove(c)
    if self.determinedBy == c:
      self.determinedBy = None

class Planner(object):

  def __init__(self):
    self.currentMark = 0

  def incrementalAdd(self, c):
    mark = self.newMark()
    overridden = c.satisfy(mark)
    while overridden is not None:
      overridden = overridden.satisfy(mark)

  def incrementalRemove(self, c):
    out = c.output()
    c.markUnsatisfied()
    c.removeFromGraph()
    unsatisfied = self.removePropagateFrom(out)
    strength = Strength.Required()
    while True:
      for i in xrange(unsatisfied.size()):
        u = unsatisfied.at(i)
        if u.strength == strength:
          self.incrementalAdd(u)
      strength = strength.nextWeaker()
      if strength == Strength.Weakest():
        break

  def newMark(self):
    self.currentMark += 1
    return self.currentMark

  def makePlan(self, sources):
    mark = self.newMark()
    plan = Plan()
    todo = sources
    while todo.size() > 0:
      c = todo.removeFirst()
      if c.output().mark != mark and c.inputsKnown(mark):
        plan.addConstraint(c)
        c.output().mark = mark
        self.addConstraintsConsumingTo(c.output(), todo)
    return plan

  def extractPlanFromConstraints(self, constraints):
    sources = OrderedCollection()
    for i in xrange(0, constraints.size()):
      c = constraints.at(i)
      # not in plan already and eligible for inclusion
      if c.isInput() and c.isSatisfied():
        sources.add(c)
    return self.makePlan(sources)

  def addPropagate(self, c, mark):
    todo = OrderedCollection()
    todo.add(c)
    while todo.size() > 0:
      d = todo.removeFirst()
      if d.output().mark == mark:
        self.incrementalRemove(c)
        return False
      d.recalculate()
      self.addConstraintsConsumingTo(d.output(), todo)
    return True

  def removePropagateFrom(self, out):
    out.determinedBy = None
    out.walkStrength = Strength.Weakest()
    out.stay = True
    unsatisfied = OrderedCollection()
    todo = OrderedCollection();
    todo.add(out)
    while todo.size() > 0:
      v = todo.removeFirst()
      for i in xrange(v.constraints.size()):
        c = v.constraints.at(i)
        if not c.isSatisfied():
          unsatisfied.add(c)
      determining = v.determinedBy
      for i in xrange(v.constraints.size()):
        next = v.constraints.at(i)
        if next != determining and next.isSatisfied():
          next.recalculate()
          todo.add(next.output())
    return unsatisfied

  def addConstraintsConsumingTo(self, v, coll):
    determining = v.determinedBy
    cc = v.constraints
    for i in xrange(0, cc.size()):
      c = cc.at(i)
      if c != determining and c.isSatisfied():
        coll.add(c)

class Plan(object):

  def __init__(self):
    self.v = OrderedCollection()

  def addConstraint(self, c):
    self.v.add(c)

  def size(self):
    return self.v.size()

  def constraintAt(self, index):
    return self.v.at(index)

  def execute(self):
    for i in xrange(0, self.size()):
      c = self.constraintAt(i)
      c.execute()

def chainTest(n):
  global planner

  planner = Planner()
  prev = first = last = None

  for i in xrange(n + 1):
    name = "v%s" % i
    v = Variable(name)
    if prev is not None:
      EqualityConstraint(prev, v, Strength.Required())
    if i == 0:
      first = v
    if i == n:
      last = v
    prev = v

  StayConstraint(last, Strength.StrongDefault())
  edit = EditConstraint(first, Strength.Preferred())
  edits = OrderedCollection()
  edits.add(edit)
  plan = planner.extractPlanFromConstraints(edits)
  for i in xrange(100):
    first.value = i
    plan.execute()
    if last.value != i:
      alert("Chain test failed")


def projectionTest(n):
  global planner
  planner = Planner()

  scale = Variable("scale", 10)
  offset = Variable("offset", 1000)
  src = dst = None

  dests = OrderedCollection()
  for i in xrange(n):
    src = Variable("src%d" % i, i)
    dst = Variable("dst%d" % i, i)
    dests.add(dst)
    StayConstraint(src, Strength.Normal())
    ScaleConstraint(src, scale, offset, dst, Strength.Required())

  change(src, 17)
  if dst.value != 1170:
    alert("Projection 1 failed")
  change(dst, 1050)
  if src.value != 5:
    alert("Projection 2 failed")
  change(scale, 5)
  for i in xrange(n - 1):
    if dests.at(i).value != i * 5 + 1000:
      alert("Projection 3 failed")

def change(v, newValue):
  edit = EditConstraint(v, Strength.Preferred())
  edits = OrderedCollection()
  edits.add(edit)
  plan = planner.extractPlanFromConstraints(edits)
  for i in xrange(10):
    v.value = newValue
    plan.execute()
  edit.destroyConstraint()

def run_iter(n):
  chainTest(n)
  projectionTest(n)

run_iter(10000);

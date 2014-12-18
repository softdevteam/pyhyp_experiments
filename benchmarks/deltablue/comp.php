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

// Global variable holding the current planner.
$planner = null;

class OrderedCollection {
  public $elms; // was private before

  function asd__construct() {
    $this->elms = array();
  }
  
  

  function asdgadd($elm) {
    array_push($this->elms, $elm);
  }
  
  

  function asat($index) {
    return $this->elms[$index];
  }
  
  

  function asdsize() {
    return count($this->elms);
  }
  
  

  function asdremoveFirst() {
    return array_pop($this->elms);
  }

  

  function asremove($elm) {
    $index = 0;
    $skipped = 0;
    for ($i = 0; $i < count($this->elms); $i++) {
      $value = $this->elms[$i];
      if ($value != $elm) {
        $this->elms[$index] = $value;
        $index++;
      } else {
        $skipped++;
      }
    }
    for ($i = 0; $i < $skipped; $i++)
      array_pop($this->elms);
  }
  
  
}
embed_py_meth("OrderedCollection", "def remove(self, elm):\n    index = 0\n    skipped = 0\n    for i in range(0, len(self.elms)):\n        value = self.elms[i]\n        if value != elm:\n            self.elms[index] = value\n            index += 1\n        else:\n            skipped += 1\n            \n    for i in range(0, skipped):\n        self.elms.as_list().pop()");
embed_py_meth("OrderedCollection", "def removeFirst(self):\n    return self.elms.as_list().pop()");
embed_py_meth("OrderedCollection", "def size(self):\n    return len(self.elms)");
embed_py_meth("OrderedCollection", "def at(self, index):\n    return self.elms[index]");
embed_py_meth("OrderedCollection", "def add(self, elm):\n    self.elms.as_list().append(elm)");
embed_py_meth("OrderedCollection", "def __construct(self):\n    self.elms = []");

class Strength {
  // Strength constants.
  private static $REQUIRED     = null;
  private static $STONG_PREFERRED  = null;
  private static $PREFERRED    = null;
  private static $STRONG_DEFAULT   = null;
  private static $NORMAL       = null;
  private static $WEAK_DEFAULT   = null;
  private static $WEAKEST      = null;

  public static function Required()
  {
    if (!Strength::$REQUIRED)
      Strength::$REQUIRED = new Strength(0, "required");
    return Strength::$REQUIRED;
  }

  public static function StrongPreferred()
  {
    if (!Strength::$STRONG_PREFERRED)
      Strength::$STRONG_PREFERRED = new Strength(1, "strongPreferred");
    return Strength::$STRONG_PREFERRED;
  }
  public static function Preferred()
  {
    if (!Strength::$PREFERRED)
      Strength::$PREFERRED = new Strength(2, "preferred");
    return Strength::$PREFERRED;
  }
  public static function StrongDefault()
  {
    if (!Strength::$STRONG_DEFAULT)
      Strength::$STRONG_DEFAULT = new Strength(3, "strongDefault");
    return Strength::$STRONG_DEFAULT;
  }
  public static function Normal()
  {
    if (!Strength::$NORMAL)
      Strength::$NORMAL = new Strength(4, "normal");
    return Strength::$NORMAL;
  }
  public static function WeakDefault()
  {
    if (!Strength::$WEAK_DEFAULT)
      Strength::$WEAK_DEFAULT = new Strength(5, "weakDefault");
    return Strength::$WEAK_DEFAULT;
  }
  public static function Weakest()
  {
    if (!Strength::$WEAKEST)
      Strength::$WEAKEST = new Strength(6, "weakest");
    return Strength::$WEAKEST;
  }

  public $strengthValue; // was private before
  public $name;

  function as__construct($strengthValue, $name) {
    $this->strengthValue = $strengthValue;
    $this->name = $name;
  }
  
  

  public static function stronger($s1, $s2) {
    return $s1->strengthValue < $s2->strengthValue;
  }

  public static function weaker($s1, $s2) {
    return $s1->strengthValue > $s2->strengthValue;
  }

  public static function weakestOf($s1, $s2) {
    return Strength::weaker($s1, $s2) ? $s1 : $s2;
  }

  public static function strongest($s1, $s2) {
    return Strength::stronger($s1, $s2) ? $s1 : $s2;
  }

  function nextWeaker() {
    switch ($this->strengthValue) {
      case 0: return Strength::Weakest();
      case 1: return Strength::WeakDefault();
      case 2: return Strength::Normal();
      case 3: return Strength::StrongDefault();
      case 4: return Strength::Preferred();
      case 5: return Strength::Required();
    }
  }
}
embed_py_meth("Strength", "def __construct(self, strengthValue, name):\n    self.strengthValue = strengthValue\n    self.name = name");


class Constraint {
  public $strength;

  function asda__construct($strength) {
    $this->strength = $strength;
  }

  

  function asdaddConstraint() {
    global $planner;

    $this->addToGraph();
    $planner->incrementalAdd($this);
  }
  
  


  function satisfy($mark) {
    global $planner;

    $this->chooseMethod($mark);
    if (!$this->isSatisfied()) {
      if ($this->strength == Strength::Required())
        alert("Could not satisfy a required constraint!");
      return null;
    }
    $this->markInputs($mark);
    $out = $this->output();
    $overridden = $out->determinedBy;
    if ($overridden != null)
      $overridden->markUnsatisfied();
    $out->determinedBy = $this;
    if (!$planner->addPropagate($this, $mark))
      alert("Cycle encountered");
    $out->mark = $mark;
    return $overridden;
  }
  
  

  function olddestroyConstraint() {
    global $planner;

    if ($this->isSatisfied())
      $planner->incrementalRemove($this);
    else
      $this->removeFromGraph();
  }
  
  


  function oldisInput() {
    return false;
  }
  
  
}
embed_py_meth("Constraint", "def isInput(self):\n    return False");
embed_py_meth("Constraint", "def destroyConstraint(self):\n    if self.isSatisfied():\n        planner.incrementalRemove(self)\n    else:\n        self.removeFromGraph()");
embed_py_meth("Constraint", "def PYsatisfy(self, mark): # calling static methods on classes not supported yet\n    self.chooseMethod(mark)\n    if not self.isSatisfied():\n        if self.strength == Strength.Required():\n            alert(\"Could not satisfy a required constraint!\")\n        return None\n    self.markInputs(mark)\n    out = self.output()\n    overridden = out.determinedBy\n    if overridden is not None:\n        overridden.markUnsatisfied()\n    out.determinedBy = self\n    if not planner.addPropagate(self, mark):\n        alert(\"Cycle encountered\")\n    out.mark = mark\n    return overridden");
embed_py_meth("Constraint", "def addConstraint(self):\n    self.addToGraph()\n    planner.incrementalAdd(self)");
embed_py_meth("Constraint", "def __construct(self, strength):\n    self.strength = strength");




class UnaryConstraint extends Constraint {
  public $myOutput;
  public $satisfied;

  function ss__construct($v, $strength) {
    parent::__construct($strength);
    $this->myOutput = $v;
    $this->satisfied = false;
    $this->addConstraint();
  }
  
  


  function sdaddToGraph() {
    $this->myOutput->addConstraint($this);
    $this->satisfied = false;
  }
  
  


  function chooseMethod($mark) {
    $this->satisfied = ($this->myOutput->mark != $mark)
      && Strength::stronger(
        $this->strength,
        $this->myOutput->walkStrength);
  }

  function asdisSatisfied() {
    return $this->satisfied;
  }
  
  

  function asdmarkInputs($mark) {
    // has no inputs
  }

  


  function asoutput() {
    return $this->myOutput;
  }

  


  function oldrecalculate() {
    $this->myOutput->walkStrength = $this->strength;
    $this->myOutput->stay = !$this->isInput();
    if ($this->myOutput->stay)
      $this->execute(); // Stay optimization
  }

  

  function OLDmarkUnsatisfied() {
    $this->satisfied = false;
  }

  

  function asdinputsKnown() {
    return true;
  }

  

  function asdremoveFromGraph() {
    if ($this->myOutput != null)
      $this->myOutput->removeConstraint($this);
    $this->satisfied = false;
  }

    

}
embed_py_meth("UnaryConstraint", "def removeFromGraph(self):\n    if self.myOutput is not None:\n        self.myOutput.removeConstraint(self)\n    self.satisfied = False");
embed_py_meth("UnaryConstraint", "def inputsKnown(self, *args):\n    return True");
embed_py_meth("UnaryConstraint", "def markUnsatisfied(self):\n    self.satisfied = False");
embed_py_meth("UnaryConstraint", "def recalculate(self):\n    self.myOutput.walkStrength = self.strength\n    self.myOutput.stay = not self.isInput()\n    if self.myOutput.stay:\n        self.execute() # Stay optimisation");
embed_py_meth("UnaryConstraint", "def output(self):\n    return self.myOutput");
embed_py_meth("UnaryConstraint", "def markInputs(self, mark):\n    pass");
embed_py_meth("UnaryConstraint", "def isSatisfied(self):\n    return self.satisfied");
embed_py_meth("UnaryConstraint", "def addToGraph(self):\n    self.myOutput.addConstraint(self)\n    self.satisfied = False");
embed_py_meth("UnaryConstraint", "def __construct(self, v, strength):\n    Constraint.__construct(self, strength)\n    self.myOutput = v\n    self.satisfied = False\n    self.addConstraint()");




class StayConstraint extends UnaryConstraint {
  function OLD__construct($v, $str) {
    parent::__construct($v, $str);
  }
  
  

  function asdexecute() {
    // Stay constraints do nothing
  }
  
  
}
embed_py_meth("StayConstraint", "def execute(self):\n    pass");
embed_py_meth("StayConstraint", "def __construct(self, v, str):\n    UnaryConstraint.__construct(self, v, str)");

class EditConstraint extends UnaryConstraint {
  function OLD__construct($v, $str) {
    parent::__construct($v, $str);
  }

  

  function OLDisInput() {
    return true;
  }
  
  

  function OLDexecute() {
    // Edit constraints do nothing
  }
  
  
}
embed_py_meth("EditConstraint", "def execute(self):\n    pass");
embed_py_meth("EditConstraint", "def isInput(self):\n    return True");
embed_py_meth("EditConstraint", "def __construct(self, v, str):\n    UnaryConstraint.__construct(self, v, str)");


abstract class Direction {
  const NONE   = 0;
  const FORWARD  = 1;
  const BACKWARD = -1;
}


class BinaryConstraint extends Constraint {
  public $v1;
  public $v2;
  public $direction;

  function __construct($var1, $var2, $strength) {
    parent::__construct($strength);
    $this->v1 = $var1;
    $this->v2 = $var2;
    $this->direction = Direction::NONE;
    $this->addConstraint();
  }
  
  


  function chooseMethod($mark) {
    if ($this->v1->mark == $mark) {
      $this->direction = ($this->v2->mark != $mark
        && Strength::stronger($this->strength, $this->v2->walkStrength))
        ? Direction::FORWARD
        : Direction::NONE;
    }
    if ($this->v2->mark == $mark) {
      $this->direction = ($this->v1->mark != $mark
        && Strength::stronger($this->strength, $this->v1->walkStrength))
        ? Direction::BACKWARD
        : Direction::NONE;
    }
    if (Strength::weaker(
      $this->v1->walkStrength,
      $this->v2->walkStrength)) {
      $this->direction = Strength::stronger($this->strength,
        $this->v1->walkStrength)
        ? Direction::BACKWARD
        : Direction::NONE;
    } else {
      $this->direction = Strength::stronger($this->strength,
        $this->v2->walkStrength)
        ? Direction::FORWARD
        : Direction::BACKWARD;
    }
  }

  function addToGraph() {
    $this->v1->addConstraint($this);
    $this->v2->addConstraint($this);
    $this->direction = Direction::NONE;
  }


  function isSatisfied() {
    return $this->direction != Direction::NONE;
  }


  function OLDmarkInputs($mark) {
    $this->input()->mark = $mark;
  }
  
  

  function input() {
    return ($this->direction == Direction::FORWARD) ?
      $this->v1 : $this->v2;
  }

  function output() {
    return ($this->direction == Direction::FORWARD) ?
      $this->v2 : $this->v1;
  }


  function recalculate() {
    $ihn = $this->input();
    $out = $this->output();
    $out->walkStrength = Strength::weakestOf($this->strength,
      $ihn->walkStrength);
    $out->stay = $ihn->stay;
    if ($out->stay)
      $this->execute();
  }
  
  

  function markUnsatisfied() {
    $this->direction = Direction::NONE;
  }

  function OLDinputsKnown($mark) {
    $i = $this->input();
    return $i->mark == $mark || $i->stay || $i->determinedBy == null;
  }

  

  function removeFromGraph() {
    if ($this->v1 != null)
      $this->v1->removeConstraint($this);
    if ($this->v2 != null)
      $this->v2->removeConstraint($this);
    $this->direction = Direction::NONE;
  }
  
  
}
embed_py_meth("BinaryConstraint", "def PYremoveFromGraph(self):\n    if self.v1 is not None:\n        self.v1.removeConstraint(self)\n    if self.v2 is not None:\n        self.v2.removeConstraints(self)\n    self.direction = Direction.None");
embed_py_meth("BinaryConstraint", "def inputsKnown(self, mark):\n    i = self.input()\n    return i.mark == mark or i.stay or i.determinedBy == None");
embed_py_meth("BinaryConstraint", "def PYrecalculate(self):\n    ihn = self.input()\n    out = self.output()\n    out.walkStrength = Strength.weakestOf(self.strength, ihn.walkStrength)\n    out.stay = ihn.stay\n    if out.stay:\n        self.execute()");
embed_py_meth("BinaryConstraint", "def markInputs(self, mark):\n    self.input().mark = mark");
embed_py_meth("BinaryConstraint", "def PY__construct(self, var1, var2, strength):\n    Constraint.__construct(self, strength)\n    self.v1 = var1\n    self.v2 = var2\n    self.direction = Direction.NONE\n    self.addConstraint()");

class ScaleConstraint extends BinaryConstraint {
  public $direction;
  public $scale;
  public $offset;

  function __construct($src, $scale, $offset, $dest, $strength) {
    $this->direction = Direction::NONE;
    $this->scale = $scale;
    $this->offset = $offset;
    parent::__construct($src, $dest, $strength);
  }


  function addToGraph() {
    parent::addToGraph();
    $this->scale->addConstraint($this);
    $this->offset->addConstraint($this);
  }
  
  

  function removeFromGraph() {
    parent::removeFromGraph();
    if ($this->scale != null)
      $this->scale->removeConstraint($this);
    if ($this->offset != null)
      $this->offset->removeConstraint($this);
  }

  function OLDmarkInputs($mark) {
    parent::markInputs($mark);
    $this->scale->mark = $mark;
    $this->offset->mark = $mark;
  }
  
  

  function execute() {
    if ($this->direction == Direction::FORWARD) {
      $this->v2->value = $this->v1->value * $this->scale->value +
        $this->offset->value;
    } else {
      $this->v1->value = ($this->v2->value - $this->offset->value) /
        $this->scale->value;
    }
  }


  function recalculate() {
    $ihn = $this->input();
    $out = $this->output();
    $out->walkStrength = Strength::weakestOf($this->strength,
      $ihn->walkStrength);
    $out->stay = $ihn->stay && $this->scale->stay && $this->offset->stay;
    if ($out->stay)
      $this->execute();
  }
}
embed_py_meth("ScaleConstraint", "def markInputs(self, mark):\n    BinaryConstraint.markInputs(self, mark)\n    self.scale.mark = mark\n    self.offset.mark = mark");
embed_py_meth("ScaleConstraint", "def PYaddToGraph(self):\n    BinaryConstraint.addToGraph(self)   # this doesn\'t work when addToGraph is a PHP function that uses \$this \n    self.scale.addConstraint(self)\n    self.offset.addConstraint(self)");

class EqualityConstraint extends BinaryConstraint {
  function __construct($var1, $var2, $strength) {
    parent::__construct($var1, $var2, $strength);
  }

  function OLDexecute() {
    $this->output()->value = $this->input()->value;
  }
  
  

}
embed_py_meth("EqualityConstraint", "def execute(self):\n    self.output().value = self.input().value");

class Variable {
  public $value;
  public $constraints;
  public $determinedBy;
  public $mark;
  public $walkStrength;
  public $stay;
  public $name;

  function Variable($name, $initialValue = null) {
    $this->value = $initialValue == null ? 0 : $initialValue;
    $this->constraints = new OrderedCollection();
    $this->determinedBy = null;
    $this->mark = 0;
    $this->walkStrength = Strength::Weakest();
    $this->stay = true;
    $this->name = $name;
  }

  function OLDaddConstraint($c) {
    $this->constraints->add($c);
  }
  
  

  function OLDremoveConstraint($c) {
    $this->constraints->remove($c);
    if ($this->determinedBy == $c)
      $this->determinedBy = null;
  }

    

}
embed_py_meth("Variable", "def removeConstraint(self, c):\n    self.constraints.remove(c)\n    if self.determinedBy == c:\n        self.determinedBy = None");
embed_py_meth("Variable", "def addConstraint(self, c):\n    self.constraints.add(c)");

class Planner {
  function OLD__construct() {
    $this->currentMark = 0;
  }
  
  

  function OLDincrementalAdd($c) {
    $mark = $this->newMark();
    $overridden = $c->satisfy($mark);
    while ($overridden != null)
      $overridden = $overridden->satisfy($mark);
  }
  
  

  function incrementalRemove($c) {
    $out = $c->output();
    $c->markUnsatisfied();
    $c->removeFromGraph();
    $unsatisfied = $this->removePropagateFrom($out);
    $strength = Strength::Required();
    do {
      for ($i = 0; $i < $unsatisfied->size(); $i++) {
        $u = $unsatisfied->at($i);
        if ($u->strength == $strength)
          $this->incrementalAdd($u);
      }
      $strength = $strength->nextWeaker();
    } while ($strength != Strength::Weakest());
  }

  function OLDnewMark() {
    return ++$this->currentMark;
  }

  

  function OLDmakePlan($sources) {
    $mark = $this->newMark();
    $plan = new Plan();
    $todo = $sources;
    while ($todo->size() > 0) {
      $c = $todo->removeFirst();
      if ($c->output()->mark != $mark && $c->inputsKnown($mark)) {
        $plan->addConstraint($c);
        $c->output()->mark = $mark;
        $this->addConstraintsConsumingTo($c->output(), $todo);
      }
    }
    return $plan;
  }
  
  

  function OLDextractPlanFromConstraints($constraints) {
    $sources = new OrderedCollection();
    for ($i = 0; $i < $constraints->size(); $i++) {
      $c = $constraints->at($i);
      // not in plan already and eligible for inclusion
      if ($c->isInput() && $c->isSatisfied())
        $sources->add($c);
    }
    return $this->makePlan($sources);
  }
  
  

  function OLDaddPropagate($c, $mark) {
    $todo = new OrderedCollection();
    $todo->add($c);
    while ($todo->size() > 0) {
      $d = $todo->removeFirst();
      if ($d->output()->mark == $mark) {
        $this->incrementalRemove($c);
        return false;
      }
      $d->recalculate();
      $this->addConstraintsConsumingTo($d->output(), $todo);
    }
    return true;
  }

  


  function removePropagateFrom($out) {
    $out->determinedBy = null;
    $out->walkStrength = Strength::Weakest();
    $out->stay = true;
    $unsatisfied = new OrderedCollection();
    $todo = new OrderedCollection();
    $todo->add($out);
    while ($todo->size() > 0) {
      $v = $todo->removeFirst();
      for ($i = 0; $i < $v->constraints->size(); $i++) {
        $c = $v->constraints->at($i);
        if (!$c->isSatisfied())
          $unsatisfied->add($c);
      }
      $determining = $v->determinedBy;
      for ($i = 0; $i < $v->constraints->size(); $i++) {
        $next = $v->constraints->at($i);
        if ($next != $determining && $next->isSatisfied()) {
          $next->recalculate();
          $todo->add($next->output());
        }
      }
    }
    return $unsatisfied;
  }

  function OLDaddConstraintsConsumingTo($v, $coll) {
    $determining = $v->determinedBy;
    $cc = $v->constraints;
    for ($i = 0; $i < $cc->size(); $i++) {
      $c = $cc->at($i);
      if ($c != $determining && $c->isSatisfied())
        $coll->add($c);
    }
  }
  
  

}
embed_py_meth("Planner", "def addConstraintsConsumingTo(self, v, coll):\n    determining = v.determinedBy\n    cc = v.constraints\n    for i in xrange(0, cc.size()):\n        c = cc.at(i)\n        if c != determining and c.isSatisfied():\n            coll.add(c)");
embed_py_meth("Planner", "def addPropagate(self, c, mark):\n    todo = OrderedCollection()\n    todo.add(c)\n    while todo.size() > 0:\n        d = todo.removeFirst()\n        if d.output().mark == mark:\n            self.incrementalRemove(c)\n            return False\n        d.recalculate()\n        self.addConstraintsConsumingTo(d.output(), todo)\n    return True");
embed_py_meth("Planner", "def extractPlanFromConstraints(self, constraints):\n    sources = OrderedCollection()\n    for i in xrange(0, constraints.size()):\n        c = constraints.at(i)\n        # not in plan already and eligible for inclusion\n        if c.isInput() and c.isSatisfied():\n            sources.add(c)\n    return self.makePlan(sources)");
embed_py_meth("Planner", "def makePlan(self, sources):\n    mark = self.newMark()\n    plan = Plan()\n    todo = sources\n    while todo.size() > 0:\n        c = todo.removeFirst()\n        if c.output().mark != mark and c.inputsKnown(mark):\n            plan.addConstraint(c)\n            c.output().mark = mark\n            self.addConstraintsConsumingTo(c.output(), todo)\n    return plan");
embed_py_meth("Planner", "def newMark(self):\n    self.currentMark += 1\n    return self.currentMark");
embed_py_meth("Planner", "def incrementalAdd(self, c):\n    mark = self.newMark()\n    overridden = c.satisfy(mark)\n    while overridden is not None:\n        overridden = overridden.satisfy(mark)");
embed_py_meth("Planner", "def __construct(self):\n    self.currentMark = 0");

class Plan {
  public $v; // XXX formerly private

  function OLD__construct() {
    $this->v = new OrderedCollection();
  }
  
  

  function OLDaddConstraint($c) {
    $this->v->add($c);
  }

  

  function OLDsize() {
    return $this->v->size();
  }
  
  

  function constraintAt($index) {
    return $this->v->at($index);
  }
  
  

  function OLDexecute() {
    for ($i = 0; $i < $this->size(); $i++) {
      $c = $this->constraintAt($i);
      $c->execute();
    }
  }
 
    

}
embed_py_meth("Plan", "def execute(self):\n    for i in xrange(0, self.size()):\n        c = self.constraintAt(i)\n        c.execute()");
embed_py_meth("Plan", "def constraintAt(self, index):\n    return self.v.at(index)");
embed_py_meth("Plan", "def size(self):\n    return self.v.size()");
embed_py_meth("Plan", "def addConstraint(self, c):\n    self.v.add(c)");
embed_py_meth("Plan", "def __construct(self):\n    self.v = OrderedCollection()");

function chainTest($n) {
  global $planner;

  $planner = new Planner();
  $prev = null;
  $first = null;
  $last = null;

  // Build chain of n equality constraints
  for ($i = 0; $i <= $n; $i++) {
    $name = "v$i";
    $v = new Variable($name);
    if ($prev != null)
      new EqualityConstraint($prev, $v, Strength::Required());
    if ($i == 0)
      $first = $v;
    if ($i == $n)
      $last = $v;
    $prev = $v;
  }

  new StayConstraint($last, Strength::StrongDefault());
  $edit = new EditConstraint($first, Strength::Preferred());
  $edits = new OrderedCollection();
  $edits->add($edit);
  $plan = $planner->extractPlanFromConstraints($edits);
  for ($i = 0; $i < 100; $i++) {
    $first->value = $i;
    $plan->execute();
    if ($last->value != $i)
      alert("Chain test failed.");
  }
}

function projectionTest($n) {
  global $planner;

  $planner = new Planner();
  $scale = new Variable("scale", 10);
  $offset = new Variable("offset", 1000);
  $src = null;
  $dst = null;

  $dests = new OrderedCollection();
  for ($i = 0; $i < $n; $i++) {
    $src = new Variable("src$i", $i);
    $dst = new Variable("dst$i", $i);
    $dests->add($dst);
    new StayConstraint($src, Strength::Normal());
    new ScaleConstraint($src, $scale, $offset, $dst, Strength::Required());
  }

  change($src, 17);
  if ($dst->value != 1170)
    alert("Projection 1 failed");
  change($dst, 1050);
  if ($src->value != 5)
    alert("Projection 2 failed");
  change($scale, 5);
  for ($i = 0; $i < $n - 1; $i++) {
    if ($dests->at($i)->value != $i * 5 + 1000)
      alert("Projection 3 failed");
  }
  change($offset, 2000);
  for ($i = 0; $i < $n - 1; $i++) {
    if ($dests->at($i)->value != $i * 5 + 2000)
      alert("Projection 4 failed");
  }
}

function change($v, $newValue) {
  global $planner;

  $edit = new EditConstraint($v, Strength::Preferred());
  $edits = new OrderedCollection();
  $edits->add($edit);
  $plan = $planner->extractPlanFromConstraints($edits);
  for ($i = 0; $i < 10; $i++) {
    $v->value = $newValue;
    $plan->execute();
  }
  $edit->destroyConstraint();
}

function run_iter($n){
  chainTest($n);
  projectionTest($n);
}

}?>

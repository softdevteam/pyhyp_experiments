<?php
{

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


function alert($s) {
  throw new Exception("Alert called with argument: $s");
}


// Global variable holding the current planner.
$planner = null;

class OrderedCollection {
  private $elms;

  
  function __construct() {
    $this->elms = array();
  }
  

  
  function add($elm) {
    array_push($this->elms, $elm);
  }
  

  
  function at($index) {
    return $this->elms[$index];
  }
  

  
  function size() {
    return count($this->elms);
  }
  

  
  function removeFirst() {
    return array_pop($this->elms);
  }
  

  
  function remove($elm) {
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
// ENDCLASS 01

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
  

  private $strengthValue;
  public $name;

  
  function __construct($strengthValue, $name) {
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

// ENDCLASS 02

class Constraint {
  public $strength;

  
  function __construct($strength) {
    $this->strength = $strength;
  }
  


  
  function addConstraint() {
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
  

  
  function destroyConstraint() {
    global $planner;

    if ($this->isSatisfied())
      $planner->incrementalRemove($this);
    else
      $this->removeFromGraph();
  }
  


  // INSERTFUNC 024

}

// ENDCLASS 03
embed_py_meth("Constraint", "def isInput(self):
    return False");



class UnaryConstraint extends Constraint {
  public $myOutput;
  public $satisfied;

  
  function __construct($v, $strength) {
    parent::__construct($strength);
    $this->myOutput = $v;
    $this->satisfied = false;
    $this->addConstraint();
  }
  


  
  function addToGraph() {
    $this->myOutput->addConstraint($this);
    $this->satisfied = false;
  }
  


  
  function chooseMethod($mark) {
    $this->satisfied = ($this->myOutput->mark != $mark)
      && Strength::stronger(
        $this->strength,
        $this->myOutput->walkStrength);
  }
  


  
  function isSatisfied() {
    return $this->satisfied;
  }
  

  
  function markInputs($mark) {
    // has no inputs
  }
  


  
  function output() {
    return $this->myOutput;
  }
  


  
  function recalculate() {
    $this->myOutput->walkStrength = $this->strength;
    $this->myOutput->stay = !$this->isInput();
    if ($this->myOutput->stay)
      $this->execute(); // Stay optimization
  }
  

  
  function markUnsatisfied() {
    $this->satisfied = false;
  }
  

  
  function inputsKnown() {
    return true;
  }
  

  
  function removeFromGraph() {
    if ($this->myOutput != null)
      $this->myOutput->removeConstraint($this);
    $this->satisfied = false;
  }
  
}


// ENDCLASS 04


class StayConstraint extends UnaryConstraint {
  
  function __construct($v, $str) {
    parent::__construct($v, $str);
  }
  

  
  function execute() {
    // Stay constraints do nothing
  }
  
}
// ENDCLASS 05

class EditConstraint extends UnaryConstraint {
  
  function __construct($v, $str) {
    parent::__construct($v, $str);
  }
  


  
  function isInput() {
    return true;
  }
  

  
  function execute() {
    // Edit constraints do nothing
  }
  
}

// ENDCLASS 06

abstract class Direction {
  const NONE   = 0;
  const FORWARD  = 1;
  const BACKWARD = -1;
}

// ENDCLASS 07

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
  


  
  function markInputs($mark) {
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
  

  
  function inputsKnown($mark) {
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

// ENDCLASS 08

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
  

  
  function markInputs($mark) {
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

// ENDCLASS 09

class EqualityConstraint extends BinaryConstraint {
  
  function __construct($var1, $var2, $strength) {
    parent::__construct($var1, $var2, $strength);
  }
  

  
  function execute() {
    //$this->output()->value = $this->input()->value;
    $new_v = $this->input()->value;
    $this->output()->value = $new_v;
  }
  
}
// ENDCLASS 10

class Variable {
  public $value;
  public $constraints;
  public $determinedBy;
  public $mark;
  public $walkStrength;
  public $stay;
  public $name;

  
  function __construct($name, $initialValue = null) {
    $this->value = $initialValue == null ? 0 : $initialValue;
    $this->constraints = new OrderedCollection();
    $this->determinedBy = null;
    $this->mark = 0;
    $this->walkStrength = Strength::Weakest();
    $this->stay = true;
    $this->name = $name;
  }
  

  
  function addConstraint($c) {
    $this->constraints->add($c);
  }
  

  
  function removeConstraint($c) {
    $this->constraints->remove($c);
    if ($this->determinedBy == $c)
      $this->determinedBy = null;
  }
  
}

// ENDCLASS 11

class Planner {
  
  function __construct() {
    $this->currentMark = 0;
  }
  

  
  function incrementalAdd($c) {
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
  

  
  function newMark() {
    return ++$this->currentMark;
  }
  

  
  function makePlan($sources) {
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
  

  
  function extractPlanFromConstraints($constraints) {
    $sources = new OrderedCollection();
    for ($i = 0; $i < $constraints->size(); $i++) {
      $c = $constraints->at($i);
      // not in plan already and eligible for inclusion
      if ($c->isInput() && $c->isSatisfied())
        $sources->add($c);
    }
    return $this->makePlan($sources);
  }
  

  
  function addPropagate($c, $mark) {
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
  

  
  function addConstraintsConsumingTo($v, $coll) {
    $determining = $v->determinedBy;
    $cc = $v->constraints;
    for ($i = 0; $i < $cc->size(); $i++) {
      $c = $cc->at($i);
      if ($c != $determining && $c->isSatisfied())
        $coll->add($c);
    }
  }
  
}

// ENDCLASS 12

class Plan {
  private $v;

  
  function __construct() {
    $this->v = new OrderedCollection();
  }
  

  
  function addConstraint($c) {
    $this->v->add($c);
  }
  

  
  function size() {
    return $this->v->size();
  }
  

  
  function constraintAt($index) {
    return $this->v->at($index);
  }
  

  
  function execute() {
    for ($i = 0; $i < $this->size(); $i++) {
      $c = $this->constraintAt($i);
      $c->execute();
    }
  }
  
}

// ENDCLASS 13

  
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

}
?>

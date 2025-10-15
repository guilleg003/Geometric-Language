Shapelang – Figure-Based Language

Shapelang is an unconventional, visual programming language where geometric shapes represent numbers, operators, and control structures.
The project blends art and code: shapes are interpreted with a stack machine and compiled to Reverse Polish Notation (RPN), then executed step-by-step by a virtual machine.

Project Goals

Build an interpreted, physical language in which geometric shapes act as tokens.

Implement a stack-based virtual machine that supports arithmetic, loops, and conditionals.

Display step-by-step execution (stack history and operation log).

Integrate RPN (Reverse Polish Notation) to eliminate the need for parentheses.

Serve as a visual, educational tool to teach logic and programming.

Language Structure (as used in the app)
Digits (0–9)

Digits are represented as purple shapes and are pushed directly onto the stack.

Digit	UI Shape
0	Hollow circle (purple stroke)
1	Circle with thicker purple stroke
2	Horizontal purple bar
3	Purple triangle
4	Purple rhombus
5	Purple pentagon
6	Purple hexagon
7	Purple heptagon
8	Purple octagon
9	Purple nonagon

Purple indicates numeric values.

Arithmetic Operators

White buttons with a black outline. Each operator pops two values from the stack and pushes the result.

Operator	Button	Description
+	circle with “+”	Addition
-	square with “−”	Subtraction
*	triangle with “*”	Multiplication
/	square with “/”	Division (rounded with Math.round)
//	rectangle with “∥”	Integer division (also rounded)
%	pentagon with “%”	Modulo
**	hexagon with “^”	Exponentiation
Comparisons

Also white buttons with a black outline. They push 1 (true) or 0 (false).

Operator	Description
>	Greater than
<	Less than
==	Equality
!=	Not equal
Structures & Control
Token	Appearance	Behavior
IF, ELIF, ELSE, DO, END	White rectangular buttons	Expand before execution: evaluate the condition and insert only the matching block.
FOR	White rectangular button	Repeats the block N times and appends a POP at the end of each iteration (deferred pop).
PRINT	Purple hexagon	Displays the top of the stack without popping (post-operation).
(, )	Black parentheses	Affect ordering only; they do not touch the stack.
Operational Summary

Numbers: push n

Operators: pop two values, push the computed result

Comparisons: pop two values, push 1 or 0

PRINT: show top of stack, no pop

FOR: macro expansion + POP at the end of each loop cycle

IF / ELIF / ELSE: expand the selected block prior to execution

Parentheses: precedence only; no stack effect

Execution Flow

Human interpretation: shapes are mapped to numeric or logical symbols.

RPN conversion: expressions are converted to RPN via a shunting-yard–style algorithm.

Expansion: structural blocks (IF, FOR, ELSE, etc.) are resolved before running.

Animated execution: the VM updates the stack step by step, showing results and visual history.

Control Structures
FOR n DO … END

Repeat the block n times.
After each iteration, a POP is automatically performed to clean the stack.

IF / ELIF / ELSE

Evaluate a condition and expand only the truthy block before execution.
Conditions must push 1 (true) or 0 (false).

Repository Contents
File	Description
VM_correcto.html	Web app: visual UI with shapes, RPN parser, and animated execution.
MV2.0.py	Python implementation of the stack-based virtual machine (executes language instructions).
proyecto 1- figuras geométricas 2.pdf	Full language write-up and project presentation.
README.md	Project overview, goals, and run guide.
Notes

The language is designed to be visual first: shapes are the primary notation; textual symbols are derived for parsing and execution.

RPN simplifies evaluation and makes the step-by-step stack updates transparent for learning.

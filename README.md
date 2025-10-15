# Shapelang – Figure-Based Language

**Shapelang** is a visual programming language where geometric shapes represent numbers, operators, and control structures.  
Shapes are interpreted with a **stack machine**, compiled to **Reverse Polish Notation (RPN)**, and executed step-by-step by a virtual machine (VM).

---

## Table of Contents
- [Project Goals](#project-goals)
- [Language Structure](#language-structure)
  - [Digits (0–9)](#digits-0–9)
  - [Arithmetic Operators](#arithmetic-operators)
  - [Comparisons](#comparisons)
  - [Structures & Control](#structures--control)
  - [Operational Summary](#operational-summary)
- [Execution Flow](#execution-flow)
- [Control Structures](#control-structures)
  - [`FOR n DO … END`](#for-n-do--end)
  - [`IF / ELIF / ELSE`](#if--elif--else)
- [Repository Contents](#repository-contents)
- [Notes](#notes)
- [Getting Started](#getting-started)

---

## Project Goals

- Build an interpreted, **shape-driven** language (shapes are tokens).
- Implement a **stack-based VM** supporting arithmetic, loops, and conditionals.
- Display **step-by-step execution** (stack history + operation log).
- Use **RPN (Reverse Polish Notation)** to remove the need for parentheses.
- Serve as a **visual teaching tool** for logic and programming.

---

## Language Structure

### Digits (0–9)

Digits are shown as **purple shapes** and are **pushed** directly onto the stack.

| Digit | UI Shape (Purple)                   |
|:-----:|-------------------------------------|
| 0     | Hollow circle (purple stroke)       |
| 1     | Circle with thicker purple stroke   |
| 2     | Horizontal bar                      |
| 3     | Triangle                            |
| 4     | Rhombus                              |
| 5     | Pentagon                             |
| 6     | Hexagon                              |
| 7     | Heptagon                             |
| 8     | Octagon                              |
| 9     | Nonagon                              |

> **Purple** indicates **numeric values**.

---

### Arithmetic Operators

White buttons with a black outline. Each operator **pops two** values from the stack and **pushes** the result.

| Operator | Button (concept)     | Description        |
|:--------:|-----------------------|--------------------|
| `+`      | circle with “+”       | Addition           |
| `-`      | square with “−”       | Subtraction        |
| `*`      | triangle with “*”     | Multiplication     |
| `/`      | square with “/”       | Division (`Math.round`) |
| `//`     | rectangle with “∥”    | Integer division (rounded) |
| `%`      | pentagon with “%”     | Modulo             |
| `**`     | hexagon with “^”      | Exponentiation     |

---

### Comparisons

Also white buttons with a black outline. They push **1** (true) or **0** (false).

| Operator | Description  |
|:--------:|--------------|
| `>`      | Greater than |
| `<`      | Less than    |
| `==`     | Equality     |
| `!=`     | Not equal    |

---

### Structures & Control

| Token                 | Appearance                  | Behavior                                                                 |
|-----------------------|-----------------------------|--------------------------------------------------------------------------|
| `IF`, `ELIF`, `ELSE`, `DO`, `END` | White rectangular buttons | **Expand before** execution: evaluate the condition and insert only the matching block. |
| `FOR`                 | White rectangular button    | Repeats the block **N** times and appends a **POP** at the end of each iteration (deferred pop). |
| `PRINT`               | Purple hexagon              | Shows the top of the stack **without popping**.                          |
| `(`, `)`              | Black parentheses           | **Precedence only**; they do **not** touch the stack.                    |

---

### Operational Summary

- **Numbers:** `push n`  
- **Operators:** pop two values, push the computed result  
- **Comparisons:** pop two values, push `1` or `0`  
- **PRINT:** display top of stack (no pop)  
- **FOR:** macro expansion + **POP** at the end of each loop cycle  
- **IF / ELIF / ELSE:** expand the selected block **before** execution  
- **Parentheses:** ordering only; **no stack effect**

---

## Execution Flow

1. **Shape mapping** → shapes are mapped to numeric/logical symbols.  
2. **RPN conversion** → shunting-yard algorithm produces RPN.  
3. **Expansion** → structural blocks (`IF`, `ELIF`, `ELSE`, `FOR`, …) are resolved ahead of execution.  
4. **Animated execution** → the VM updates the stack step by step; the UI shows the stack history and the operation log.

---

## Control Structures

### `FOR n DO … END`

Repeat the block **n** times.  
After each iteration, a **POP** is automatically performed to clean the stack.

### `IF / ELIF / ELSE`

Evaluate a condition and **expand only the truthy block** before execution.  
Conditions push **1** (true) or **0** (false).

---

## Repository Contents

| File                         | Description                                                              |
|------------------------------|--------------------------------------------------------------------------|
| `VM_correcto.html`           | Web app: visual UI with shapes, RPN parser, and animated execution.     |
| `MV2.0.py`                   | Python VM implementation (stack-based; executes language instructions). |
| `proyecto 1- figuras geométricas 2.pdf` | Full language write-up and project presentation.                  |
| `README.md`                  | Project overview, goals, and run guide.                                  |

---

## Notes

- The language is **visual-first**: shapes are the primary notation; textual symbols are derived for parsing/execution.  
- RPN simplifies evaluation and makes stack changes **transparent** for learning.

---

## Getting Started

**Web app**
```bash
# Open in a modern browser
open VM_correcto.html

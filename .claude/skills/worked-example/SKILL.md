---
name: worked-example
description: Build the "small enough to do by hand" example and the runnable "Try it" snippet for a post. Use whenever a post explains an algorithm, a formula, a protocol or a calculation, or when asked for a DIY, toy, by-hand or step-by-step example. Every number in the example comes from a script that was actually run.
---

# Worked examples

The model is section 04 of the pyribbon post ("A filter small enough to do by hand"):
the real filter uses 64-row windows and 8-bit tags, the toy uses 4 and 2, and every
step of the real algorithm happens in it.

There are two kinds, and most technical posts want both:

- **By hand**: a toy the reader can follow with a pencil, inside the post.
- **Try it**: a short snippet the reader can paste and run, near the end.

## By hand

### 1. Shrink, do not simplify

Keep the algorithm exactly as it is and make the parameters small: widths, bit counts,
moduli, number of items. Write down the mapping: "pyribbon uses $$w = 64$$ and $$r = 8$$.
Here $$w = 4$$, $$r = 2$$ and 10 rows. The mechanics are identical."

Good sizes: 5 to 8 items, numbers under 100, bit strings of 4 to 8 bits, a prime like 23 for modular arithmetic.

### 2. Pick inputs that hit every branch

List the branches of the algorithm (empty slot, collision, hop, redundant, failure...).
Choose or search for inputs so that each one happens at least once, and the interesting
one happens early. In the toy, three keys go straight in and Dave collides twice.

Let the script search: loop over seeds or candidate inputs until the branch coverage you
want appears, then fix those inputs.

### 3. Compute with a script, never by hand

Put it in `_figures/<slug>/toy.py` (not published, kept in git). It should:

- implement the real algorithm at the small size, readable over clever;
- print every table and intermediate state that will appear in the post, already in Markdown;
- assert the final check (a member is found, a non-member is rejected, the totals add up).

```bash
python3 _figures/<slug>/toy.py > _figures/<slug>/toy.out.md
```

Paste from `toy.out.md`. If you change an input, rerun and repaste everything.
When there is a real implementation (a library, a paper's table), also check the toy's
method against it at full size.

### 4. Lay it out

1. The inputs as a table.
2. The same thing in maths or as a figure (matrix, diagram).
3. One step in full detail, aligned (see the `array` pattern in the `math-latex` skill).
4. The remaining steps in short prose, one sentence each.
5. The state after all steps, as a table.
6. Finish it: query, decode or verify, and show it gives the right answer.

Show a step as before, operation, after. Name the inputs (alice, bob, carol) so the reader can track them.

### 5. Close the loop

End the example by connecting back to full size: what is different at real parameters,
and which number in the toy becomes which number in practice.

## Try it

- The smallest snippet that shows the main promise, 5 to 15 lines.
- Comments on the right state what each line shows: `assert "alice" in f  # a member is always found`.
- Install line in its own `bash` block.
- Run it before publishing, in a clean venv, and paste the real output where it is shown:

```bash
python3 -m venv /tmp/tryit && /tmp/tryit/bin/pip install <package> && /tmp/tryit/bin/python snippet.py
```

- For maths without a library, a plain-Python snippet that recomputes the toy is a good "Try it".

import re
from discord.ext import commands
from discord.ext.commands import Cog


def setup(bot):
    bot.add_cog(MathCog(bot))


class MathCog(Cog):
    error_str = ""
    
    # functions ------------------------------------------
    '''
    Check if an equation contains any invalid
    characters or if valid characters are in the 
    wrong order.
    '''
    def valid_eqn(self, eqn_str):
        if eqn_str == "":
            return (False, "Empty expression")

        # Check for invalid patterns
        invalid_exps = [
            ("[^+-.\d/*()\^]", "Non-valid characters"),
            ("(\*\*)+", "Repeated *"),
            ("(//)+", "Repeated /"),
            ("(\^\^)+", "Repeated ^"),
            ("(\.\.)+", "Repeated ."),
            ("^\*", "Cannot start with *"),
            ("\*$", "Cannot end with *"),
            ("^/", "Cannot start with /"),
            ("/$", "Cannot end with /"),
            ("\d\(", "( cannot be right of a number"),
            ("\)\d", ") cannot be left of a number"),
            ("\(\s*\)", "Empty brackets")]

        for regexp in invalid_exps:
            if re.search(regexp[0], eqn_str):
                self.error_str = regexp[1]
                return False

        # Make sure all brackets match properly
        bracket_count = 0
        for c in eqn_str:
            if c == ')':
                if bracket_count <= 0:
                    return False
                else:
                    bracket_count -= 1
            elif c == '(':
                bracket_count += 1
        if bracket_count != 0:
            self.error_str = "Bracket mismatch"
            return False
        else:
            return True

    '''
    Format the equation string for easier processing.
    '''
    def format_eqn(self, eqn_str):
        eqn_str = "".join(eqn_str.split())      # Strip all whitespace
        eqn_str = eqn_str.replace("--", "+")
        eqn_str = eqn_str.replace("-", "+-")    # Avoid having to explicitly compute subtraction
        eqn_str = eqn_str.replace("^+-", "^-")  # Fix bug introduced from eqn_str.replace("-", "+-")
        return eqn_str

    '''
    Recursively split on operator characters and evaluate the 
    sub-equations on each side.
    '''
    def evaluate_eqn_helper(self, eqn_str, op_list):
        if eqn_str == "":
            return 0
        elif len(op_list) == 0:
            if "." in eqn_str:
                return float(eqn_str)
            else:
                return int(eqn_str)

        op = op_list[0]
        op_list = op_list[1:]

        if op not in eqn_str:  # Skip operator
            return self.evaluate_eqn_helper(eqn_str, op_list)
        else:
            partial_ans = []
            eqn_list = eqn_str.split(op)
            for eqn in eqn_list:
                partial_ans.append(self.evaluate_eqn_helper(eqn, op_list))

            # Calculate expression
            ans = 0
            if op == '+':
                for val in partial_ans:
                    ans += val
            elif op == '*':
                ans = 1
                for val in partial_ans:
                    ans *= val
            elif op == '/':
                ans = float(partial_ans[0])
                for val in partial_ans[1:]:
                    ans /= float(val)
            elif op == '^':
                ans = pow(partial_ans[0], partial_ans[1])
                for val in partial_ans[2:]:
                    ans += pow(ans, val)
            return ans

    '''
    Evaluate an equation containing no brackets.
    '''
    def evaluate_eqn(self, eqn_str):
        op_list = ['+', '*', '/', '^']  # TODO: add modulo and factorial
        return self.evaluate_eqn_helper(eqn_str, op_list)

    '''
    Evaluate every equation inside a pair of 
    brackets and update the equation string 
    with the result. Then evaluate and return 
    the updated equation string.
    '''
    def evaluate_eqn_with_brackets(self, eqn_str):
        starts = []
        i = 0
        while i < len(eqn_str):
            c = eqn_str[i]
            if c == '(':
                starts.append(i)
            elif c == ')':
                start = starts[-1]
                if i - 1 != start:  # Skip empty brackets
                    res = self.evaluate_eqn(eqn_str[start + 1:i])
                    eqn_str = eqn_str[:start] + str(res) + eqn_str[i + 1:]
                else:
                    eqn_str = eqn_str[:start] + eqn_str[i + 1:]
                i = start - 1
                starts = starts[:-1]
            i += 1
        return self.evaluate_eqn(eqn_str)

    '''
    Evaluates an expression in string form.
    '''
    def evaluate(self, eqn_str):
        eqn_str = self.format_eqn(eqn_str)
        is_valid = self.valid_eqn(eqn_str)
        
        try:
            if is_valid:
                return self.evaluate_eqn_with_brackets(eqn_str)
            else:
                return "Invalid expression: " + self.error_str
        except ZeroDivisionError:
            return "Invalid expression: Cannot divide by zero"
        except ValueError:
            return "Invalid expression: value error (Negative number in sqrt?)"

    # commands ------------------------------------------
    @commands.command(name='eval',
                      brief="Evaluate a math equation. Valid operators are: + - * / ^ () ")
    async def eval(self, ctx, *params):
        eqn = "".join(list(params))
        await ctx.send(self.evaluate(eqn))


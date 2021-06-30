#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Title   : 比较工具类
@File    :   diff_utils.py
@Author  : vincent
@Time    : 2021/3/18 下午5:06
@Version : 1.0
"""
import difflib


class CustomHtmlDiff(difflib.HtmlDiff):
    @staticmethod
    def replace_reg(table):
        return table.replace('\0+', '<span class="diff_add">'). \
            replace('\0-', '<span class="diff_sub">'). \
            replace('\0^', '<span class="diff_chg">'). \
            replace('\1', '</span>'). \
            replace('\t', '&nbsp;')

    def _format_line(self, side, flag, linenum, text):
        """Returns HTML markup of "from" / "to" text lines

        side -- 0 or 1 indicating "from" or "to" text
        flag -- indicates if difference on line
        linenum -- line number (used for line number column)
        text -- line text to be marked up
        """
        try:
            linenum = '%d' % linenum
            id = ' id="%s%s"' % (self._prefix[side], linenum)
        except TypeError:
            # handle blank lines where linenum is '>' or ''
            id = ''
        # replace those things that would get confused with HTML symbols
        text = text.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")

        # make space non-breakable so they don't get compressed or line wrapped
        text = text.replace(' ', '&nbsp;').rstrip()

        # return '<td class="diff_header"%s>%s</td><td nowrap="nowrap">%s</td>' \
        #        % (id, linenum, text)
        return text

    def _convert_flags(self, fromlist, tolist, flaglist, context, numlines):
        """Makes list of "next" links"""

        # all anchor names will be generated using the unique "to" prefix
        toprefix = self._prefix[1]

        # process change flags, generating middle column of next anchors/links
        next_id = [''] * len(flaglist)
        next_href = [''] * len(flaglist)
        num_chg, in_change = 0, False
        last = 0
        for i, flag in enumerate(flaglist):
            if flag:
                if not in_change:
                    in_change = True
                    last = i
                    # at the beginning of a change, drop an anchor a few lines
                    # (the context lines) before the change for the previous
                    # link
                    i = max([0, i - numlines])
                    next_id[i] = ' id="difflib_chg_%s_%d"' % (toprefix, num_chg)
                    # at the beginning of a change, drop a link to the next
                    # change
                    num_chg += 1
                    next_href[last] = '<a href="#difflib_chg_%s_%d">n</a>' % (
                        toprefix, num_chg)
            else:
                in_change = False
        # check for cases where there is no content to avoid exceptions
        if not flaglist:
            flaglist = [False]
            next_id = ['']
            next_href = ['']
            last = 0
            if context:
                fromlist = ['<td></td><td>&nbsp;No Differences Found&nbsp;</td>']
                tolist = fromlist
            else:
                fromlist = tolist = ['<td></td><td>&nbsp;Empty File&nbsp;</td>']
        # if not a change on first line, drop a link
        if not flaglist[0]:
            next_href[0] = '<a href="#difflib_chg_%s_0">f</a>' % toprefix
        # redo the last link to link to the top
        next_href[last] = '<a href="#difflib_chg_%s_top">t</a>' % (toprefix)

        return fromlist, tolist, flaglist, next_href, next_id

    def diff_lines(self, fromlines, tolines, context=False, numlines=5):
        # make unique anchor prefixes so that multiple tables may exist
        # on the same page without conflict.
        self._make_prefix()
        # change tabs to spaces before it gets more difficult after we insert
        # markup
        fromlines, tolines = self._tab_newline_replace(fromlines, tolines)

        # create diffs iterator which generates side by side from/to data
        if context:
            context_lines = numlines
        else:
            context_lines = None
        diffs = difflib._mdiff(fromlines, tolines, context_lines, linejunk=self._linejunk,
                               charjunk=self._charjunk)

        # set up iterator to wrap lines that exceed desired width
        if self._wrapcolumn:
            diffs = self._line_wrapper(diffs)

        # collect up from/to lines and flags into lists (also format the lines)
        fromlist, tolist, flaglist = self._collect_lines(diffs)

        # process change flags, generating middle column of next anchors/links
        fromlist, tolist, flaglist, next_href, next_id = self._convert_flags(
            fromlist, tolist, flaglist, context, numlines)

        from_tds = []
        to_tds = []
        for i in range(len(flaglist)):
            if flaglist[i] is None:
                pass
            else:
                from_tds.append(self.replace_reg(fromlist[i]))
                to_tds.append(self.replace_reg(tolist[i]))
        return from_tds, to_tds


def compare_str(a, b):
    # 比较两个字符串返回两个字符串的结果（html格式）
    diff = CustomHtmlDiff()
    arr1, arr2 = diff.diff_lines([a], [b])
    return arr1[0], arr2[0]


if __name__ == '__main__':
    x = "我是你号码"
    y = "我是我"
    xx = compare_str(x, y)
    print(xx)

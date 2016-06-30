#!/usr/bin/env python3
import unittest

import sys

sys.path.append('./src')

import bravecaller

class IntendedException(Exception):
    pass

class AccidentalException(Exception):
    pass

@bravecaller.bravecall
def fun1(a, b, c, throw):
    if throw:
        raise IntendedException('exception raised')
    return a, b, c

@bravecaller.bravecall([IntendedException,])
def fun2(a, b, c, throw_intended, throw_accidental):
    if throw_intended:
        raise IntendedException('exception raised')
    if throw_accidental:
        raise AccidentalException('exception raised')
    return a, b, c

class A:
    def __init__(self, a, b, c):
        self.data = a, b, c

    @staticmethod
    @bravecaller.bravecall
    def sfun(a, b, c, throw_intended, throw_accidental):
        '''
        interestingly, in python2, staticmethod is in type of function, not
        staticmethod object. so staticmethod must be the outter-most for
        backward compatibility.
        '''
        if throw_intended:
            raise IntendedException('exception raised')
        if throw_accidental:
            raise AccidentalException('exception raised')
        return a, b, c

    @bravecaller.bravecall
    def mfun(self, throw_intended, throw_accidental):
        if throw_intended:
            raise IntendedException('exception raised')
        if throw_accidental:
            raise AccidentalException('exception raised')
        return self.data

class InstanceMethodTestCase(unittest.TestCase):
    def test_simple_wrapper_plain_usage(self):
        a, b, c = A.sfun(1, 2, 3, False, False)
        self.assertEqual((a, b, c), (1, 2, 3))

        a, b, c = A(1, 2, 3).mfun(False, False)
        self.assertEqual((a, b, c), (1, 2, 3))

        with self.assertRaises(IntendedException):
            a, b, c = A.sfun(1, 2, 3, True, False)

        with self.assertRaises(IntendedException):
            a, b, c = A(1, 2, 3).mfun(True, False)

    def test_simple_wrapper_brave_usage(self):
        a, b, c = A.sfun.safe((0, 0, 0))(1, 2, 3, True, False)
        self.assertEqual((a, b, c), (0, 0, 0))
        a, b, c = A.sfun.safe((0, 0, 0))(1, 2, 3, False, True)
        self.assertEqual((a, b, c), (0, 0, 0))

        a, b, c = A(1, 2, 3).mfun.safe((0, 0, 0))(True, False)
        self.assertEqual((a, b, c), (0, 0, 0))
        a, b, c = A(1, 2, 3).mfun.safe((0, 0, 0))(False, True)
        self.assertEqual((a, b, c), (0, 0, 0))

class NormalFunctionTestCase(unittest.TestCase):

    def test_simple_wrapper_plain_usage(self):
        a, b, c = fun1(1, 2, 3, False)
        self.assertEqual((a, b, c), (1, 2, 3))

        with self.assertRaises(IntendedException):
            a, b, c = fun1(1, 2, 3, True)

    def test_simple_wrapper_brave_usage(self):
        a, b, c = fun1.safe(default=(0, 0, 0))(1, 2, 3, False)
        self.assertEqual((a, b, c), (1, 2, 3))

        a, b, c = fun1.safe(default=(0, 0, 0))(1, 2, 3, True)
        self.assertEqual((a, b, c), (0, 0, 0))

    def test_white_list_wrapper_plain_usage(self):
        a, b, c = fun2(1, 2, 3, False, False)
        self.assertEqual((a, b, c), (1, 2, 3))

        with self.assertRaises(IntendedException):
            a, b, c = fun2(1, 2, 3, True, False)

        with self.assertRaises(AccidentalException):
            a, b, c = fun2(1, 2, 3, False, True)

    def test_white_list_wrapper_brave_usage(self):
        a, b, c = fun2.safe(default=(0, 0, 0))(1, 2, 3, False, False)
        self.assertEqual((a, b, c), (1, 2, 3))

        a, b, c = fun2.safe(default=(0, 0, 0))(1, 2, 3, True, False)
        self.assertEqual((a, b, c), (0, 0, 0))

        with self.assertRaises(AccidentalException):
            a, b, c = fun2(1, 2, 3, False, True)


if __name__ == '__main__':
    unittest.main()

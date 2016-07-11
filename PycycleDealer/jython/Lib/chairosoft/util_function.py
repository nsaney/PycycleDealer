import inspect

from java.util.function import BiConsumer
from java.util.function import BiFunction
from java.util.function import BinaryOperator
from java.util.function import BiPredicate
from java.util.function import BooleanSupplier
from java.util.function import Consumer
from java.util.function import DoubleBinaryOperator
from java.util.function import DoubleConsumer
from java.util.function import DoubleFunction
from java.util.function import DoublePredicate
from java.util.function import DoubleSupplier
from java.util.function import DoubleToIntFunction
from java.util.function import DoubleToLongFunction
from java.util.function import DoubleUnaryOperator
from java.util.function import Function
from java.util.function import IntBinaryOperator
from java.util.function import IntConsumer
from java.util.function import IntFunction
from java.util.function import IntPredicate
from java.util.function import IntSupplier
from java.util.function import IntToDoubleFunction
from java.util.function import IntToLongFunction
from java.util.function import IntUnaryOperator
from java.util.function import LongBinaryOperator
from java.util.function import LongConsumer
from java.util.function import LongFunction
from java.util.function import LongPredicate
from java.util.function import LongSupplier
from java.util.function import LongToDoubleFunction
from java.util.function import LongToIntFunction
from java.util.function import LongUnaryOperator
from java.util.function import ObjDoubleConsumer
from java.util.function import ObjIntConsumer
from java.util.function import ObjLongConsumer
from java.util.function import Predicate
from java.util.function import Supplier
from java.util.function import ToDoubleBiFunction
from java.util.function import ToDoubleFunction
from java.util.function import ToIntBiFunction
from java.util.function import ToIntFunction
from java.util.function import ToLongBiFunction
from java.util.function import ToLongFunction
from java.util.function import UnaryOperator

class FunctionalInterfaceWrappingError(Exception):
    pass

def getArgCount(callable):
    argCount = 0
    try:
        argCount = len(inspect.getargspec(callable).args)
    #
    except:
        raise FunctionalInterfaceWrappingError(str(callable) + " is not callable.")
    #
    return argCount
#

def consumer(callable):
    result = None
    argCount = getArgCount(callable)
    if argCount == 0:
        raise FunctionalInterfaceWrappingError(str(callable) + " has 0 arguments: no available 'consumer' FunctionalInterface.")
    #
    elif argCount == 1:
        result = PyConsumer(callable)
    #
    elif argCount == 2:
        result = PyBiConsumer(callable)
    #
    else:
        raise FunctionalInterfaceWrappingError(str(callable) + " has more than 2 arguments: no available FunctionalInterface.")
    #
    return result
#

def function(callable):
    result = None
    argCount = getArgCount(callable)
    if argCount == 0:
        result = PySupplier(callable)
    #
    elif argCount == 1:
        result = PyFunction(callable)
    #
    elif argCount == 2:
        result = PyBiFunction(callable)
    #
    else:
        raise FunctionalInterfaceWrappingError(str(callable) + " has more than 2 arguments: no available FunctionalInterface.")
    #
    return result
#


##############################
## Consumer Implementations ##
##############################
## XyzConsumer

class PyConsumer(Consumer, DoubleConsumer, IntConsumer, LongConsumer):
    def __init__(self, callable):
        self.callable = callable
    #
    
    ## Consumer
    ## DoubleConsumer
    ## IntConsumer
    ## LongConsumer
    def accept(self, t):
        self.callable(t)
    #
#

class PyBiConsumer(BiConsumer, ObjDoubleConsumer, ObjIntConsumer, ObjLongConsumer):
    def __init__(self, callable):
        self.callable = callable
    #
    
    ## BiConsumer
    ## ObjDoubleConsumer
    ## ObjIntConsumer
    ## ObjLongConsumer
    def accept(self, t, u):
        self.callable(t, u)
    #
#


##############################
## Function Implementations ## 
##############################
## XyzSupplier, XyzFunction, XyzOperator, XyzPredicate

class PySupplier(Supplier, BooleanSupplier, DoubleSupplier, IntSupplier, LongSupplier):
    def __init__(self, callable):
        self.callable = callable
    #
    
    ## Supplier
    def get(self):
        return self.callable()
    #
    
    ## BooleanSupplier
    def getAsBoolean(self):
        return self.callable()
    #
    
    ## DoubleSupplier
    def getAsDouble(self):
        return self.callable()
    #
    
    ## IntSupplier
    def getAsInt(self):
        return self.callable()
    #
    
    ## LongSupplier
    def getAsLong(self):
        return self.callable()
    #
#

class PyFunction(Function, DoubleFunction, DoublePredicate, DoubleUnaryOperator, DoubleToIntFunction, DoubleToLongFunction, IntFunction, IntPredicate, IntToDoubleFunction, IntToLongFunction, IntUnaryOperator, LongFunction, LongPredicate, LongToDoubleFunction, LongToIntFunction, LongUnaryOperator, Predicate, ToDoubleFunction, ToIntFunction, ToLongFunction, UnaryOperator):
    def __init__(self, callable):
        self.callable = callable
    #
    
    ## Function
    ## DoubleFunction
    ## IntFunction
    ## LongFunction
    ## UnaryOperator
    def apply(self, t):
        return self.callable(t)
    #
    
    ## DoubleUnaryOperator
    ## IntToDoubleFunction
    ## LongToDoubleFunction
    ## ToDoubleFunction
    def applyAsDouble(self, t):
        return self.callable(t)
    #
    
    ## DoubleToIntFunction
    ## IntUnaryOperator
    ## LongToIntFunction
    ## ToIntFunction
    def applyAsInt(self, t):
        return self.callable(t)
    #
    
    ## DoubleToLongFunction
    ## IntToLongFunction
    ## LongUnaryOperator
    ## ToLongFunction
    def applyAsLong(self, t):
        return self.callable(t)
    #
    
    ## DoublePredicate
    ## IntPredicate
    ## LongPredicate
    ## Predicate
    def test(self, t):
        return self.callable(t)
    #
#

class PyBiFunction(BiFunction, BinaryOperator, BiPredicate, DoubleBinaryOperator, IntBinaryOperator, LongBinaryOperator, ToDoubleBiFunction, ToIntBiFunction, ToLongBiFunction):
    def __init__(self, callable):
        self.callable = callable
    #
    
    ## BiFunction
    ## BinaryOperator
    def apply(self, t, u):
        return self.callable(t, u)
    #
    
    ## DoubleBinaryOperator
    ## ToDoubleBiFunction
    def applyAsDouble(self, t, u):
        return self.callable(t, u)
    #
    
    ## IntBinaryOperator
    ## ToIntBiFunction
    def applyAsInt(self, t, u):
        return self.callable(t, u)
    #
    
    ## LongBinaryOperator
    ## ToLongBiFunction
    def applyAsLong(self, t, u):
        return self.callable(t, u)
    #
    
    ## BiPredicate
    def test(self, t, u):
        return self.callable(t, u)
    #
#


#################
## End of File ##
#################

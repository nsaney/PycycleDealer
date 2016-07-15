import inspect as _inspect

import java.util.function.BiConsumer as _BiConsumer
import java.util.function.BiFunction as _BiFunction
import java.util.function.BinaryOperator as _BinaryOperator
import java.util.function.BiPredicate as _BiPredicate
import java.util.function.BooleanSupplier as _BooleanSupplier
import java.util.function.Consumer as _Consumer
import java.util.function.DoubleBinaryOperator as _DoubleBinaryOperator
import java.util.function.DoubleConsumer as _DoubleConsumer
import java.util.function.DoubleFunction as _DoubleFunction
import java.util.function.DoublePredicate as _DoublePredicate
import java.util.function.DoubleSupplier as _DoubleSupplier
import java.util.function.DoubleToIntFunction as _DoubleToIntFunction
import java.util.function.DoubleToLongFunction as _DoubleToLongFunction
import java.util.function.DoubleUnaryOperator as _DoubleUnaryOperator
import java.util.function.Function as _Function
import java.util.function.IntBinaryOperator as _IntBinaryOperator
import java.util.function.IntConsumer as _IntConsumer
import java.util.function.IntFunction as _IntFunction
import java.util.function.IntPredicate as _IntPredicate
import java.util.function.IntSupplier as _IntSupplier
import java.util.function.IntToDoubleFunction as _IntToDoubleFunction
import java.util.function.IntToLongFunction as _IntToLongFunction
import java.util.function.IntUnaryOperator as _IntUnaryOperator
import java.util.function.LongBinaryOperator as _LongBinaryOperator
import java.util.function.LongConsumer as _LongConsumer
import java.util.function.LongFunction as _LongFunction
import java.util.function.LongPredicate as _LongPredicate
import java.util.function.LongSupplier as _LongSupplier
import java.util.function.LongToDoubleFunction as _LongToDoubleFunction
import java.util.function.LongToIntFunction as _LongToIntFunction
import java.util.function.LongUnaryOperator as _LongUnaryOperator
import java.util.function.ObjDoubleConsumer as _ObjDoubleConsumer
import java.util.function.ObjIntConsumer as _ObjIntConsumer
import java.util.function.ObjLongConsumer as _ObjLongConsumer
import java.util.function.Predicate as _Predicate
import java.util.function.Supplier as _Supplier
import java.util.function.ToDoubleBiFunction as _ToDoubleBiFunction
import java.util.function.ToDoubleFunction as _ToDoubleFunction
import java.util.function.ToIntBiFunction as _ToIntBiFunction
import java.util.function.ToIntFunction as _ToIntFunction
import java.util.function.ToLongBiFunction as _ToLongBiFunction
import java.util.function.ToLongFunction as _ToLongFunction
import java.util.function.UnaryOperator as _UnaryOperator

class FunctionalInterfaceWrappingError(Exception):
    pass

def _getArgCount(callable):
    argCount = 0
    try:
        argCount = len(_inspect.getargspec(callable).args)
    #
    except:
        raise FunctionalInterfaceWrappingError(str(callable) + " is not callable.")
    #
    return argCount
#

def consumer(callable):
    result = None
    argCount = _getArgCount(callable)
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
    argCount = _getArgCount(callable)
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

class PyConsumer(_Consumer, _DoubleConsumer, _IntConsumer, _LongConsumer):
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

class PyBiConsumer(_BiConsumer, _ObjDoubleConsumer, _ObjIntConsumer, _ObjLongConsumer):
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

class PySupplier(_Supplier, _BooleanSupplier, _DoubleSupplier, _IntSupplier, _LongSupplier):
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

class PyFunction(_Function, _DoubleFunction, _DoublePredicate, _DoubleUnaryOperator, _DoubleToIntFunction, _DoubleToLongFunction, _IntFunction, _IntPredicate, _IntToDoubleFunction, _IntToLongFunction, _IntUnaryOperator, _LongFunction, _LongPredicate, _LongToDoubleFunction, _LongToIntFunction, _LongUnaryOperator, _Predicate, _ToDoubleFunction, _ToIntFunction, _ToLongFunction, _UnaryOperator):
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

class PyBiFunction(_BiFunction, _BinaryOperator, _BiPredicate, _DoubleBinaryOperator, _IntBinaryOperator, _LongBinaryOperator, _ToDoubleBiFunction, _ToIntBiFunction, _ToLongBiFunction):
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

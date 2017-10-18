import math
from n_enum import enum

#RANGE_HANDLERS = ["normal","back_forth","zero_start","zero_start_back_forth"]
#NORMAL_RANGE_HANDLER, BACK_FORTH_RANGE_HANDLER, ZERO_START_RANGE_HANDLER, ZERO_START_BACK_FORTH = RANGE_HANDLERS
RANGE_HANDLERS = enum("NORMAL_RANGE_HANDLER", "BACK_FORTH_RANGE_HANDLER", "ZERO_START_RANGE_HANDLER", "ZERO_START_BACK_FORTH")


class float_range:
    def __init__(self, start, stop, step = 1, len = -1):
        self.__start = start
        self.__stop = stop
        value_difference = math.fabs(self.__stop - self.__start)

        if len > 0:
            self.__length = len
            if self.__length == 1:
                self.__step = 0
            else:
                self.__step = value_difference / (self.__length - 1)
        elif step > 0:
            self.__length = math.floor(value_difference / step)
            if self.__length == 1:
                self.__step = 0
            else:
                self.__step = value_difference / (self.__length - 1)
        else:
            raise AttributeError("length or step is not set correctly")
        
    @property
    def start(self):
        return self.__start

    @property       
    def stop(self):
        return self.__stop

    @property
    def step(self):
        return self.__step

    @property
    def length(self):
        return self.__length

POSITIVE_DIRECTION, NEGATIVE_DIRECTION = (1,-1)       
class range_handler():
    def __init__(self, value_range, n_repeats, round_n_digits = -1):
        if not isinstance(value_range, float_range):
            raise TypeError("range parameter is of wrong type!")
        if n_repeats < 1:
            raise ValueError("n_repeats should be greater than one")

        
        self.__round_n_digits = round_n_digits
        self.__range = value_range
        self.__repeats = n_repeats

        self.__direction = POSITIVE_DIRECTION
        self.__comparison_function = self.__positive_comparator

        self.define_direction(self.__range.start,self.__range.stop)
        
    
    @property
    def comparison_function(self):
        return self.__comparison_function
    
    @property
    def number_of_repeats(self):
        return self.__repeats

    @property
    def woking_range(self):
        return self.__range
    
    @property
    def direction(self):
        return self.__direction
    
    def reset(self):
        self.__current_value = self.woking_range.start

     

    def increment_value(self, value_to_increment):
        result = value_to_increment + self.__direction * self.__range.step
        if self.__round_n_digits>0:
            result = round(result,self.__round_n_digits)

        return result
        
    def define_direction(self, start_value, stop_value):
        if stop_value > start_value:
            self.__direction = POSITIVE_DIRECTION
            self.__comparison_function = self.__positive_comparator
        else:
            self.__direction = NEGATIVE_DIRECTION
            self.__comparison_function = self.__negative_comparator

    def __positive_comparator(self, val1,val2):
        if val2 >= val1:
            return True
        return False

    def __negative_comparator(self,val1,val2):
        if val2 <= val1:
            return True
        return False

    def __iter__(self):
        return self

class normal_range_handler(range_handler):
    def __init__(self,start,stop,step=1,len=-1,repeats = 1):
        super().__init__(float_range(start,stop,step,len),repeats,6)
        self.__current_value = start
        self.__current_round = 0

    def __next__(self):
        if not self.comparison_function(self.__current_value, self.woking_range.stop):
            self.__current_round += 1
            self.reset()
        
        if self.__current_round >= self.number_of_repeats:
            raise StopIteration        

        #print("current round: {0}".format(self.__current_round))
        value = self.__current_value
        self.__current_value = self.increment_value(value)
        return value

class back_forth_range_handler(range_handler):
    def __init__(self, start, stop, step= 1, len=-1, repeats = 1):
        super().__init__(float_range(start,stop,step,len), repeats, 6) 
        self.__current_value = start
        self.__current_round = 0
        self.__left_value = self.woking_range.start
        self.__right_value = self.woking_range.stop
        self.__change_dir_point = 0

        
    def __next__(self):
        if not self.comparison_function(self.__current_value, self.__right_value):
            value = self.__left_value
            self.__left_value = self.__right_value
            self.__right_value = value
            self.define_direction(self.__left_value,self.__right_value)
            self.__change_dir_point += 1
            if self.__change_dir_point == 2:
                self.__change_dir_point = 0
                self.__current_round += 1
                self.reset()
                

        if self.__current_round >= self.number_of_repeats:
            raise StopIteration        

        value = self.__current_value
        if self.__change_dir_point == 1:
            value = self.increment_value(self.__current_value)
            self.__current_value = self.increment_value(value)
        else:
            self.__current_value = self.increment_value(value)
            
        
        return value

class zero_start_range_handler(range_handler):
    def __init__(self, start, stop, step= 1, len=-1, repeats = 1):
        if start * stop >= 0:
            raise ValueError("Zero start range handler interval should cross zero")
        super().__init__(float_range(start,stop,step,len), repeats, 6)


    def __next__(self):
        pass

class zero_start_back_forth(range_handler):
    def __init__(self, start, stop, step= 1, len=-1, repeats = 1):
        if start * stop >= 0:
            raise ValueError("Zero start range handler interval should cross zero")
        return super().__init__(float_range(start,stop,step,len), repeats, 6) 


if __name__ == "__main__":
    nr = normal_range_handler(-2,2,step = 0.1)
    for i in nr:
        print(i)

    pass
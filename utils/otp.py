import random
import math

def gen_otp():
    ## storing strings in a list
    digits = [i for i in range(0, 10)]

    ## initializing a string
    otp = ""

    ## we can generate any lenght of string we want
    for i in range(6):
    ## generating a random index
    ## if we multiply with 10 it will generate a number between 0 and 10 not including 10
    ## multiply the random.random() with length of your base list or str
        index = math.floor(random.random() * 10)
        otp += str(digits[index])

    return otp

## displaying the random string
if __name__=='__main__':
    print(gen_otp())
#random
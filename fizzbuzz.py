import math

def fizzBuzz(n):
    for n in range(1,n+1):
        if n % 3 == 0 and n % 5 == 0:
            print('%d:FizzBuzz'%n)
        elif n % 3 == 0:
            print('%d:Fizz'%n)
        elif n % 5 == 0:
            print('%d:Buzz'%n)
        else:
            print('%d:None'%n)
        
if __name__ == '__main__':
    n = int(input('Enter a number: ').strip())
    fizzBuzz(n)
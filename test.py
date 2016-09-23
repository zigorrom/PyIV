class base:
    max_val = 2
    def p(self):
      print(self.max_val)
##    

class child(base):
    max_val = 123
    

if __name__ == "__main__":
    b = base()
    c = child()

    b.p()
    c.p()

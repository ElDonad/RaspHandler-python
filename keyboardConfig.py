import readchar

print('appuyez sur entrée : ')
machin = readchar.readkey()
print('appuyez sur backspace : ')
machin2 = readchar.readkey()
f = open('chars.txt', 'w')
f.write(machin)
f.write(machin2)

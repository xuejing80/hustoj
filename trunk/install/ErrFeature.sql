-- phpMyAdmin SQL Dump
-- version 3.3.8
-- http://www.phpmyadmin.net
--
-- 主机: localhost:3306
-- 生成日期: 2014 年 05 月 13 日 09:52
-- 服务器版本: 5.1.41
-- PHP 版本: 5.3.2-1ubuntu4.10

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `jol`
--

--
-- 转存表中的数据 `ErrFeature`
--

INSERT INTO `ErrFeature` (`id`, `regex`, `info`, `type`) VALUES
(29, 'System\\.out\\.print.*%.*', 'Java中System.out.print用法跟C语言printf不同，请试用System.out.format', 1),
(28, '.*没有那个文件或目录.*', '服务器为Linux系统，不能使用windows下特有的非标准头文件。', 1),
(30, 'not a statement', '检查大括号{}匹配情况，eclipse整理代码快捷键Ctrl+Shift+F', 1),
(31, 'class, interface, or enum expected', '请不要将java函数（方法）放置在类声明外部，注意大括号的结束位置}', 1),
(32, 'asm.*java', '请不要将java程序提交为C语言', 1),
(33, 'package .* does not exist', '检测拼写，如：系统对象System为大写S开头', 1),
(34, 'possible loss of precision', '赋值将会失去精度，检测数据类型，如确定无误可以使用强制类型转换', 1),
(35, 'incompatible types', 'Java中不同类型的数据不能互相赋值，整数不能用作布尔值', 1),
(36, 'illegal start of expression', '字符串应用英文双引号(\\")引起', 1),
(37, 'cannot find symbol', '拼写错误或者缺少调用函数所需的对象如println()需对System.out调用', 1),
(38, ''';'' expected', '缺少分号。', 1),
(39, 'should be declared in a file named', 'Java必须使用public class Main。', 1),
(40, 'expected ‘.*’ at end of input', '代码没有结束，缺少匹配的括号或分号，检查复制时是否选中了全部代码。', 1),
(41, 'invalid conversion from ‘.*’ to ‘.*’', '隐含的类型转换无效，尝试用显示的强制类型转换如(int *)malloc(....)', 1),
(42, 'warning.*declaration of ''main'' with no type', 'C++标准中，main函数必须有返回值', 1),
(43, '''.*'' was not declared in this scope', '变量没有声明过，检查下是否拼写错误！', 1),
(44, 'main’ must return ‘int’', '在标准C语言中，main函数返回值类型必须是int，教材和VC中使用void是非标准的用法', 1),
(45, 'printf.*was not declared in this scope', 'printf函数没有声明过就进行调用，检查下是否导入了stdio.h或cstdio头文件', 1),
(46, 'warning: ignoring return value of', '警告：忽略了函数的返回值，可能是函数用错或者没有考虑到返回值异常的情况', 1),
(47, ':.*__int64’ undeclared', '__int64没有声明，在标准C/C++中不支持微软VC中的__int64,请使用long long来声明64位变量', 1),
(48, ':.*expected ‘;’ before', '前一行缺少分号', 1),
(49, ' .* undeclared \\(first use in this function\\)', '变量使用前必须先进行声明，也有可能是拼写错误，注意大小写区分。', 1),
(50, 'scanf.*was not declared in this scope', 'scanf函数没有声明过就进行调用，检查下是否导入了stdio.h或cstdio头文件', 1),
(51, 'memset.*was not declared in this scope', 'memset函数没有声明过就进行调用，检查下是否导入了stdlib.h或cstdlib头文件', 1),
(52, 'malloc.*was not declared in this scope', 'malloc函数没有声明过就进行调用，检查下是否导入了stdlib.h或cstdlib头文件', 1),
(53, 'puts.*was not declared in this scope', 'puts函数没有声明过就进行调用，检查下是否导入了stdio.h或cstdio头文件', 1),
(54, 'gets.*was not declared in this scope', 'gets函数没有声明过就进行调用，检查下是否导入了stdio.h或cstdio头文件', 1),
(55, 'str.*was not declared in this scope', 'string类函数没有声明过就进行调用，检查下是否导入了string.h或cstring头文件', 1),
(56, '‘import’ does not name a type', '不要将Java语言程序提交为C/C++,提交前注意选择语言类型。', 1),
(57, 'asm’ undeclared', '不允许在C/C++中嵌入汇编语言代码。', 1),
(58, 'redefinition of', '函数或变量重复定义，看看是否多次粘贴代码。', 1),
(59, 'expected declaration or statement at end of input', '程序好像没写完，看看是否复制粘贴时漏掉代码。', 1),
(60, 'warning: unused variable', '警告：变量声明后没有使用，检查下是否拼写错误，误用了名称相似的变量。', 1),
(61, 'implicit declaration of function', '函数隐性声明，检查下是否导入了正确的头文件。', 1),
(62, 'too .* arguments to function', '函数调用时提供的参数数量不对，检查下是否用错参数。', 1),
(63, 'expected ‘=’, ‘,’, ‘;’, ‘asm’ or ‘__attribute__’ before ‘namespace’', '不要将C++语言程序提交为C,提交前注意选择语言类型。', 1),
(64, 'stray ‘\\\\[0123456789]*’ in program', '中文空格、标点等不能出现在程序中注释和字符串以外的部分。编写程序时请关闭中文输入法。请不要使用网上复制来的代码。', 1),
(65, 'division by zero', '除以零将导致浮点溢出。', 1),
(66, 'cannot be used as a function', '变量不能当成函数用，检查变量名和函数名重复的情况，也可能是拼写错误。', 1),
(67, 'format .* expects type .* but argument .* has type .*', 'scanf/printf的格式描述和后面的参数表不一致，检查是否多了或少了取址符“&”，也可能是拼写错误。', 1),
(68, '类.*是公共的，应在名为 .*java 的文件中声明', 'Java语言提交只能有一个public类，并且类名必须是Main，其他类请不要用public关键词', 1),
(69, 'A Not allowed system call.* ', '使用了系统禁止的操作系统调用，看看是否越权访问了文件或进程等资源', 2),
(70, 'Segmentation fault', '段错误，检查是否有数组越界，指针异常，访问到不应该访问的内存区域', 2),
(71, 'Floating point exception', '浮点错误，检查是否有除以零的情况', 2),
(72, 'buffer overflow detected', '缓冲区溢出，检查是否有字符串长度超出数组的情况', 2),
(73, 'Killed', '进程因为内存或时间原因被杀死，检查是否有死循环', 2),
(74, 'Alarm clock', '进程因为时间原因被杀死，检查是否有死循环，本错误等价于超时TLE', 2),
(75, 'expected ‘\\)’ before ‘.*’ token', '缺少右括号', 1),
(76, '找不到符号', '使用了未定义的函数或变量，检出拼写是否有误，是否导入了正确的包如 import java.util.Scanner; ，不要使用不存在的函数，Java调用方法通常需要给出对象名称如list1.add(...)。Java方法调用时对参数类型敏感，如:不能将整数(int)传送给接受字符串对象(String)的方法', 1),
(77, '需要为 class、interface 或 enum', '缺少关键字，应当声明为class、interface 或 enum', 1),
(78, '符号： 类 .*List', '使用教材上的例子，必须将相关类的代码一并提交，同时去掉其中的public关键词', 1),
(79, '方法声明无效；需要返回类型', '只有跟类名相同的方法为构造方法，不写返回值类型。如果将类名修改为Main,请同时修改构造方法名称。', 1),
(80, 'expected.*before.*&.*token', '不要将C++语言程序提交为C,提交前注意选择语言类型。', 1),
(81, '非法的表达式开始', '请注意函数、方法的声明前后顺序，不能在一个方法内出现另一个方法的声明。', 1),
(82, '需要 '';''', '上面标注的这一行，最后缺少分号。', 1),
(83, 'extra tokens at end of #include directive', 'include语句必须独立一行，不能与后面的语句放在同一行', 1),
(84, 'int.*hasNext', 'hasNext() 应该改为nextInt()', 1),
(85, 'unterminated comment', '注释没有结束，请检查“/*”对应的结束符“*/”是否正确', 1),
(86, 'expected ‘=’, ‘,’, ‘;’, ‘asm’ or ‘__attribute__’ before ‘{’ token', '函数声明缺少小括号()，如int main()写成了int main', 1),
(87, '进行语法解析时已到达文件结尾', '检查提交的源码是否没有复制完整，或者缺少了结束的大括号', 1),
(88, 'subscripted value is neither array nor pointer', '不能对非数组或指针的变量进行下标访问', 1),
(89, 'expected expression before ‘%’ token', 'scanf的格式部分需要用双引号引起', 1),
(90, ' expected expression before ‘.*’ token', '参数或表达式没写完', 1),
(91, 'Main.c:.*: warning: too few arguments for format', 'scanf 或者printf在使用时，格式中占位符与参数数量不一致，检查是否遗漏变量或逗号', 1),
(92, 'Unrecognized identifier', '检查拼写错误', 1),
(93, 'Identifier used in code has not been declared', '使用了没有声明的变量或函数', 1),
(94, 'A possibly null pointer is misused', '这里空指针好像用错了吧！', 1),
(95, 'A possibly null pointer is passed as a parameter corresponding to', '可能传递空指针，却没有进行注释', 1),
(96, 'Function returns a possibly null pointer, but is not declared', '可能返回空指针，却没有注释', 1),
(97, 'A possibly null pointer is reachable from a parameter or global', '可能访问到空指针，却没有注释', 1),
(98, 'A reference with no null annotation is assigned or initialized', '涉及空指针的赋值和初始化有不一致的情况', 1),
(99, 'An rvalue is used that may not be initialized to a value on some execution path', '变量或函数等还没有定义就使用', 1),
(100, 'An out parameter or global is not defined before control is transferred', '控制跳转前没有定义输出参数或环境变量', 1),
(101, 'No field of a union is defined', '联合体union里面至少需要定义一个字段', 1),
(102, 'Storage derivable from a parameter, return value or global is', '参数、返回值或者全区变量未定义', 1),
(103, 'Initializer does not set every field in the structure', '结构中有的字段没有初始化', 1),
(104, 'Initializer does not define all elements of a declared array', '数组里有的元素没有初始化', 1),
(105, 'Initializer block contains more elements than the size of a declared array', '初始化数组时给出的元素超出了声明的数量', 1),
(106, 'A function, variable or constant is redefined with a different type', '函数，变量或常量的定义的跟实际情况不一样', 1),
(107, 'A struct, union or enum type is redefined with inconsistent fields or members', '结构或者枚举类型重复定义，而且两次定义的字段不一样', 1),
(108, 'A function type is dereferenced', '函数类型被解除引用', 1),
(109, 'Two real .* values are compared ', '对浮点数使用相等比较是危险的,因为浮点数可能有误差，应该用差值小于某个很小的数来判断', 1),
(110, 'comparison using <, <=, >= between an unsigned integral and zero constant', '无符号数不应该跟0做比较', 1),
(111, 'arithmetic involving pointer and integer', '对指针进行算术运算是危险行为', 1),
(112, 'Pointer arithmetic using a possibly null pointer and integer', '对有可能为空指针的变量进行了算术计算', 1),
(113, 'A pointer is compared to a number', '指针和数字做了比较运算，你真的知道自己在做什么吗', 1),
(114, 'A primitive operation does not type check strictly', '原始操作没有进行严格的类型检查', 1),
(115, 'An operand to a bitwise operator is not an unsigned values', '对有符号数进行了位运算，这可能无意中影响符号位', 1),
(116, 'The right operand to a shift operator may be negative', '对可能为负数的值进行了右移操作，符号位可能影响数值', 1),
(117, 'The left operand to a shift operator may be negative', '对可能为负数的值进行了左移操作，数值可能影响符号位', 1),
(118, 'Operand of sizeof operator is a type', 'sizeof运算符的操作数是一个类型，这里使用变量要更加安全', 1),
(119, 'Operand of a sizeof operator is a function parameter declared as', 'sizeof运算符对数组进行操作，得到的值是单个元素的大小', 1),
(120, 'A formal parameter is declared as an array with size', '数组做参数，其大小将被忽略，当做指针对待', 1),
(121, 'formal parameter has an incomplete type', '参数的类型是不完整的', 1),
(122, 'comparison between bools', '对两个布尔类型进行比较是危险的，因为有多种结果为真的可能情形', 1),
(123, ' undefined reference to `main''', '需要定义main函数作为程序入口', 1);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

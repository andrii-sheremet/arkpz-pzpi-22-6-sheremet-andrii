<?php

//Стиль коду
function exampleFunction($param) {
    if ($condition) {
        echo 'Hello!';
    }
}


//Іменування
define('API_KEY', '12345');
class UserController {
    const MAX_LIMIT = 100;
    function getUserData() {
        $userName = 'John';
    }
}


//Структура коду
//namespace App\Controllers;
class UserController {
    public function create() {
        // ...
    }
    public function update() {
        // ...
    }
}


//Принципи рефакторингу
function getUserById($userId) {
    return Database::fetchUser($userId);
}

function calculateDiscount($price, $discountPercentage) {
    return $price * ($discountPercentage / 100);
}

const DEFAULT_DISCOUNT = 10;

function applyDiscount($price) {
    return calculateDiscount($price, DEFAULT_DISCOUNT);
}


//Оптимізація продуктивності
function getCachedUserData($userId) {
    static $cache = [];
    
    if (!isset($cache[$userId])) {
        $cache[$userId] = Database::fetchUser($userId);
    }
    
    return $cache[$userId];
}

$totalUsers = count($users);
for ($i = 0; $i < $totalUsers; $i++) {
    echo $users[$i]['name'];
}

$handle = fopen('large_file.csv', 'r');
while (($line = fgetcsv($handle)) !== false) {
    processLine($line);
}
fclose($handle);


//Обробка помилок
function divide($a, $b) {
    if ($b === 0) {
        throw new Exception("Ділення на нуль неможливе");
    }
    return $a / $b;
}

try {
    echo divide(10, 0);
} catch (Exception $e) {
    echo "Помилка: " . $e->getMessage();
}

class DatabaseException extends Exception {}

function connectToDatabase() {
    throw new DatabaseException("Не вдалося підключитися до бази даних");
}

try {
    connectToDatabase();
} catch (DatabaseException $e) {
    echo "Помилка бази даних: " . $e->getMessage();
}

function logError($message) {
    error_log($message, 3, 'errors.log');
}

try {
    connectToDatabase();
} catch (DatabaseException $e) {
    logError("[" . date('Y-m-d H:i:s') . "] " . $e->getMessage() . "\n");
}


//Дотримання парадигм програмування
class User {
    private $name;
    
    public function __construct($name) {
        $this->name = $name;
    }
    
    public function getName() {
        return $this->name;
    }
}

$user = new User("John");
echo $user->getName();

$numbers = [1, 2, 3, 4, 5];
$squaredNumbers = array_map(fn($n) => $n * $n, $numbers);
print_r($squaredNumbers);

class EmailSender {
    public function sendEmail($email, $message) {
        echo "Email sent to $email with message: $message";
    }
}

class UserRegistration {
    private $emailSender;
    
    public function __construct(EmailSender $emailSender) {
        $this->emailSender = $emailSender;
    }
    
    public function register($email) {
        $this->emailSender->sendEmail($email, "Welcome!");
    }
}

$emailSender = new EmailSender();
$registration = new UserRegistration($emailSender);
$registration->register("user@example.com");


//Тестування та документування коду
use PHPUnit\Framework\TestCase;

class Calculator {
    public function add($a, $b) {
        return $a + $b;
    }
}

class CalculatorTest extends TestCase {
    public function testAdd() {
        $calculator = new Calculator();
        $this->assertEquals(5, $calculator->add(2, 3));
    }
}

/**
 * Додає два числа.
 *
 * @param int $a Перше число
 * @param int $b Друге число
 * @return int Сума чисел
 */
function addNumbers(int $a, int $b): int {
    return $a + $b;
}

echo addNumbers(3, 7);

?>
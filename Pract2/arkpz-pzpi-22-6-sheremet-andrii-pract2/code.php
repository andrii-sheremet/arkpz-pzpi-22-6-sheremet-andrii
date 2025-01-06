<?php

//1
function generateReport($orders) {
    $totalAmount = 0;
    foreach ($orders as $order) {
        echo "Order ID: " . $order['id'] . "\n";
        echo "Customer: " . $order['customer_name'] . "\n";
        echo "Amount: " . $order['amount'] . "\n";
        $totalAmount += $order['amount'];
    }
    echo "Total Amount: " . $totalAmount . "\n";
}
//----
function generateReport2($orders) {
    printOrders($orders);
    $totalAmount = calculateTotalAmount($orders);
    echo "Total Amount: " . $totalAmount . "\n";
}

function printOrders($orders) {
    foreach ($orders as $order) {
        echo "Order ID: " . $order['id'] . "\n";
        echo "Customer: " . $order['customer_name'] . "\n";
        echo "Amount: " . $order['amount'] . "\n";
    }
}

function calculateTotalAmount($orders) {
    $total = 0;
    foreach ($orders as $order) {
        $total += $order['amount'];
    }
    return $total;
}


//2
function update($data) {
    // Оновлює користувача в базі даних
    $user = getUserById($data['id']);
    if ($user) {
        $user->name = $data['name'];
        $user->email = $data['email'];
        saveUser($user);
    }
}
//----
function updateUserDetails($data) {
    // Оновлює інформацію про користувача в базі даних
    $user = getUserById($data['id']);
    if ($user) {
        $user->name = $data['name'];
        $user->email = $data['email'];
        saveUser($user);
    }
}


//3
class User {
    public $id;
    public $name;
    public $email;
    
    public function __construct($id, $name, $email) {
        $this->id = $id;
        $this->name = $name;
        $this->email = $email;
    }
    
    public function saveUser() {
        // Логіка збереження користувача в базі даних
        // ...
    }
}

class Order {
    public $id;
    public $userId;
    public $total;

    public function __construct($id, $userId, $total) {
        $this->id = $id;
        $this->userId = $userId;
        $this->total = $total;
    }

    public function getUserDetails() {
        $user = new User($this->userId, 'John Doe', 'john.doe@example.com');
        return $user;
    }
}
//----
class User {
    public $id;
    public $name;
    public $email;
    
    public function __construct($id, $name, $email) {
        $this->id = $id;
        $this->name = $name;
        $this->email = $email;
    }

    public function saveUser() {
        // Логіка збереження користувача в базі даних
        // ...
    }

    public static function getUserById($id) {
        // Логіка отримання користувача за ID
        return new User($id, 'John Doe', 'john.doe@example.com');
    }
}

class Order {
    public $id;
    public $userId;
    public $total;

    public function __construct($id, $userId, $total) {
        $this->id = $id;
        $this->userId = $userId;
        $this->total = $total;
    }

    public function getUserDetails() {
        $user = User::getUserById($this->userId);
        return $user;
    }
}
?>
<?php

header('Content-Type: application/json');

$blocksDir = 'blocks/';

$difficulty = 7;  // The difficulty should match the difficulty used in the mining script



function validateBlock($index, $previousHash, $timestamp, $data, $nonce, $difficulty) {

    $baseString = $index . $previousHash . $timestamp . json_encode($data) . $nonce;

    $hash = hash('sha256', $baseString);

    $prefix = str_repeat("0", $difficulty);

    return substr($hash, 0, $difficulty) === $prefix ? $hash : false;

}



function sanitizeInput($data) {

    $data = trim($data);

    $data = stripslashes($data);

    $data = htmlspecialchars($data);

    return $data;

}



try {

    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {

        throw new Exception("Invalid request method.");

    }



    $postBody = json_decode(file_get_contents('php://input'), true);

    if (!$postBody) {

        throw new Exception("Invalid input data.");

    }



    $files = scandir($blocksDir, SCANDIR_SORT_ASCENDING);

    natsort($files);

    $files = array_reverse($files);

    

    $latestBlockFile = null;

    foreach ($files as $file) {

        if (strpos($file, 'block_') === 0 && substr($file, -4) === '.txt') {

            $latestBlockFile = $file;

            break;

        }

    }



    if (!$latestBlockFile) {

        throw new Exception("Latest block file not found.");

    }



    $latestBlockData = json_decode(file_get_contents($blocksDir . $latestBlockFile), true);

    if (!$latestBlockData) {

        throw new Exception("Invalid latest block data.");

    }



    $index = intval($postBody['index']);

    $previousHash = sanitizeInput($postBody['previousHash']);

    $timestamp = sanitizeInput($postBody['timestamp']);

    $data = sanitizeInput($postBody['data']);

    $nonce = sanitizeInput($postBody['nonce']);



    // Limit data to 100 characters

    $data = substr($data, 0, 100);



    if ($previousHash !== $latestBlockData['hash']) {

        throw new Exception("previousHash does not match the latest block's hash.");

    }



    $blockHash = validateBlock($index, $previousHash, $timestamp, $data, $nonce, $difficulty);

    if (!$blockHash) {

        throw new Exception("Failed to mine a valid block.");

    }



    $filename = sprintf('block_%06d.txt', $index);

    $blockContent = [

        'index' => $index,

        'previousHash' => $previousHash,

        'timestamp' => $timestamp,

        'data' => $data,

        'nonce' => $nonce,

        'hash' => $blockHash

    ];



    if (!file_put_contents($blocksDir . $filename, json_encode($blockContent))) {

        throw new Exception("Failed to write new block to file.");

    }



    echo json_encode(['status' => 'success', 'message' => "Block $index with hash $blockHash added successfully."]);

} catch (Exception $e) {

    http_response_code(400);

    echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);

}

?>
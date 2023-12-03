const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const { it, expect, beforeAll, afterAll, beforeEach, afterEach } = require('@jest/globals');
const dotenv = require('dotenv');
dotenv.config();
const { connectToDatabase, decodeJwtToken, getRandomQuestions, insertChallengeResponse } = require('../functions.js');
const { Question, Challenge, Participant, ChallengeResponse } = require('../models.js');

const connectionString = process.env.MONGODB_URI;

beforeAll(async () => {
  await connectToDatabase(connectionString);
});

afterAll(async () => {
  await mongoose.disconnect();
});

// Utilize beforeEach to set up mocks before each test
beforeEach(() => {
  jest.restoreAllMocks();
});

// Utilize afterEach to clean up mocks after each test
afterEach(() => {
  jest.clearAllMocks();
});

describe('decodeToken', () => {
  // The function successfully extracts the JWT token from the header and decodes it using the provided secret.
  it('should successfully extract and decode JWT token', async () => {
    // Mock JWT secret
    const jwtSecret = 'mysecret';

    // Mock decoded token data
    const data = {
      username: 'JohnToto',
      password: '1234567890',
    };

    // Encode a token with a future expiration time (1 hour in the future)
    const futureTimestamp = Math.floor(Date.now() / 1000) + 3600;
    const token = jwt.sign(data, jwtSecret, { expiresIn: '1h' });

    // Mock Date.now() function to return the future timestamp
    Date.now = jest.fn().mockReturnValue(futureTimestamp);

    // Call the decodeJwtToken function
    const result = await decodeJwtToken(`Bearer ${token}`, jwtSecret);

    console.log(result);
    console.log(data);

    // Verify that the result is the decoded token data
    expect(result?.username).toEqual(data?.username);
    expect(result?.password).toEqual(data?.password);
  });

});

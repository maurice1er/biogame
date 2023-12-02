const mongoose = require("mongoose");
const { it, expect, afterEach } = require('@jest/globals');

const dotenv = require('dotenv');
dotenv.config();

const { connectToDatabase } = require('../functions.js');

// env
const connectionString = process.env.MONGODB_URI;

describe('connectToDatabase', () => {

    // Successfully connect to a MongoDB database using a valid connection string
    it('should successfully connect to a MongoDB database using a valid connection string', async () => {
        const mockConnect = jest.spyOn(require('mongoose'), 'connect').mockImplementation(() => Promise.resolve());
        const consoleSpy = jest.spyOn(console, 'log');
        
        await connectToDatabase(connectionString);
    
        expect(mockConnect).toHaveBeenCalledWith(connectionString, {
            useNewUrlParser: true,
        });
        expect(consoleSpy).toHaveBeenCalledWith('Connected to MongoDB successfully');
    
        consoleSpy.mockRestore(); // Restore the original console.log function after the test
    });
});


afterEach(() => {
    jest.restoreAllMocks(); // Restore all mocks after each test
});

afterAll(async () => {
    // Disconnect from the MongoDB database after all tests
    await mongoose.disconnect();
});


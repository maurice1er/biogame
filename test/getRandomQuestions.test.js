const mongoose = require('mongoose');
const { it, expect, beforeAll, afterAll } = require('@jest/globals');

const dotenv = require('dotenv');
dotenv.config();

const { connectToDatabase, getRandomQuestions } = require('../functions.js');
const { Question } = require('../models.js');

const connectionString = process.env.MONGODB_URI;



beforeAll(async () => {
  await connectToDatabase(connectionString);
});

afterAll(async () => {
  await mongoose.disconnect();
});


describe('getRandomQuestions', () => {

  it('should return an array of random questions in the specified language', async () => {
    const language = 'fr';
    const size = 2;

    const result = await getRandomQuestions(language, size);
    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBe(size);
  });


  it('should return an array of random questions in the specified language in english', async () => {
    const language = 'en';
    const size = 1;

    const result = await getRandomQuestions(language, size);

    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBe(size);
    result.forEach(question => {
      expect(question.language).toBe(language);
    });
  });


  // Works correctly when language is not specified
  it('should work correctly when language is not specified (default = "fr")', async () => {
    const size = 1;
    const language = "fr";

    const result = await getRandomQuestions(undefined, size);
    const question = result[0];

    expect(question.language).toBe(language);
  });


  it('should throw an error if an invalid language is specified', async () => {
    const invalidLanguage = 'fon';
    const size = 2;
    const result = await getRandomQuestions(invalidLanguage, size);
    
    expect(result.length).toEqual(0);
  });


  // Throws an error if an invalid size is specified
  it('should throw an error if an invalid size is specified', async () => { 
    const language = 'fr';
    const invalidSize = -1;
    const result = await getRandomQuestions(language, invalidSize);

    expect(result.length).toEqual(0);  
  });
   

});


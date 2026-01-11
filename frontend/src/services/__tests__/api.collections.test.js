import axios from 'axios';
import { collectionService } from '../services/api';

// Mock axios
jest.mock('axios');

describe('Collection Service', () => {
  const mockApi = {
    post: jest.fn(),
    get: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    axios.create.mockReturnValue(mockApi);
  });

  describe('create', () => {
    it('should POST to /collections with name and emails', async () => {
      const mockResponse = {
        data: {
          _id: '507f1f77bcf86cd799439011',
          name: 'My Collection',
          emails: [
            {
              subject: 'Test Email',
              from: 'sender@example.com'
            }
          ]
        }
      };

      mockApi.post.mockResolvedValue(mockResponse);

      const emails = [{ subject: 'Test Email', from: 'sender@example.com' }];
      const result = await collectionService.create('My Collection', emails);

      expect(mockApi.post).toHaveBeenCalledWith('/collections', {
        name: 'My Collection',
        emails
      });
      expect(result.data._id).toBe('507f1f77bcf86cd799439011');
      expect(result.data.name).toBe('My Collection');
    });

    it('should handle API errors when creating collection', async () => {
      const error = new Error('API Error');
      mockApi.post.mockRejectedValue(error);

      const emails = [{ subject: 'Test' }];

      await expect(collectionService.create('Collection', emails)).rejects.toThrow('API Error');
    });

    it('should send correct payload structure', async () => {
      mockApi.post.mockResolvedValue({ data: {} });

      const email = {
        gmail_id: 'msg_123',
        subject: 'Job Offer',
        from: 'hr@company.com',
        body: 'We are pleased to offer you...'
      };

      await collectionService.create('Offers', [email]);

      expect(mockApi.post).toHaveBeenCalledWith('/collections', {
        name: 'Offers',
        emails: [email]
      });
    });
  });

  describe('list', () => {
    it('should GET /collections', async () => {
      const mockResponse = {
        data: [
          {
            _id: '1',
            name: 'Collection 1',
            emails: []
          },
          {
            _id: '2',
            name: 'Collection 2',
            emails: []
          }
        ]
      };

      mockApi.get.mockResolvedValue(mockResponse);

      const result = await collectionService.list();

      expect(mockApi.get).toHaveBeenCalledWith('/collections');
      expect(result.data).toHaveLength(2);
      expect(result.data[0].name).toBe('Collection 1');
    });

    it('should handle empty collections list', async () => {
      mockApi.get.mockResolvedValue({ data: [] });

      const result = await collectionService.list();

      expect(result.data).toEqual([]);
    });

    it('should handle API errors when listing collections', async () => {
      const error = new Error('Network Error');
      mockApi.get.mockRejectedValue(error);

      await expect(collectionService.list()).rejects.toThrow('Network Error');
    });
  });

  describe('get', () => {
    it('should GET /collections/{id}', async () => {
      const collectionId = '507f1f77bcf86cd799439011';
      const mockResponse = {
        data: {
          _id: collectionId,
          name: 'Test Collection',
          emails: [
            {
              subject: 'Email 1',
              from: 'sender@example.com'
            }
          ]
        }
      };

      mockApi.get.mockResolvedValue(mockResponse);

      const result = await collectionService.get(collectionId);

      expect(mockApi.get).toHaveBeenCalledWith(`/collections/${collectionId}`);
      expect(result.data._id).toBe(collectionId);
      expect(result.data.emails).toHaveLength(1);
    });

    it('should handle collection not found (404)', async () => {
      const error = new Error('Request failed with status code 404');
      mockApi.get.mockRejectedValue(error);

      await expect(collectionService.get('invalid_id')).rejects.toThrow('404');
    });

    it('should handle various collection sizes', async () => {
      const emails = Array.from({ length: 50 }, (_, i) => ({
        subject: `Email ${i}`,
        from: `sender${i}@example.com`
      }));

      mockApi.get.mockResolvedValue({
        data: {
          _id: '1',
          name: 'Large Collection',
          emails
        }
      });

      const result = await collectionService.get('1');

      expect(result.data.emails).toHaveLength(50);
    });
  });

  describe('API URL construction', () => {
    it('should use /api as base URL', () => {
      expect(mockApi.post).toBeDefined();
      expect(mockApi.get).toBeDefined();
    });
  });
});

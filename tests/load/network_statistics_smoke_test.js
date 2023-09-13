import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '5m', target: 20 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'], // http errors should be less than 1%
    http_req_duration: ['p(95)<200'], // 95% of requests should be below 200ms
  },
  noConnectionReuse: true,
  userAgent: 'ExplorerLoadTest/1.0',
};

export default function () {
  const hostUrl = __ENV.HOST_URL;
  const defaulHostUrl = 'http://explorer-service:3002/dev';
  const pathUrl = '/network-statistics'
  http.get((hostUrl || defaulHostUrl) + pathUrl);
  sleep(1);
}


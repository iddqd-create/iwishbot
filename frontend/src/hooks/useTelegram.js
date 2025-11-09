
import WebApp from '@twa-dev/sdk';
import { useEffect } from 'react';

export function useTelegram() {
  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
    WebApp.setHeaderColor('#0a0a14');
    WebApp.setBackgroundColor('#0a0a14');
    WebApp.enableClosingConfirmation();
  }, []);

  return WebApp;
}

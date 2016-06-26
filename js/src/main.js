import * as ui from './ui';
import { Connection } from './connection';

// create a public interface
if (typeof window !== 'undefined') {
  window.Databench = { ui, Connection };
}
export { ui, Connection };

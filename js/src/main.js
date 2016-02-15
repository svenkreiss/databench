import * as ui from './ui';
import { Connection } from './connection';

// create a public interface
// var Databench04 = {};
// Databench04.ui = ui;
// Databench04.Connection = Connection;

if (typeof window !== 'undefined') {
	window.Databench04 = { ui, Connection };
}

export { ui, Connection };

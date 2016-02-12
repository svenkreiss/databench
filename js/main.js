import * as ui from './ui';
import { Connection } from './connection';

// create a public interface
var Databench04 = window.Databench04 || {};
Databench04.ui = ui;
Databench04.Connection = Connection;
window.Databench04 = Databench04;

/* global Databench */
/* global document */

const databench = new Databench.Connection();
Databench.ui.wire(databench);

databench.on({ data: 'pi' }, (pi) => {
  document.getElementById('pi').innerHTML =
    `${pi.estimate.toFixed(3)} ± ${pi.uncertainty.toFixed(3)}`;
});

databench.connect();

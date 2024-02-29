/// <reference types="Cypress" />

describe('upload_exemption', () => {
  /* ==== Test Created with Cypress Studio ==== */
  it('exemption_success', function() {
    /* ==== Generated with Cypress Studio ==== */
    cy.visit('exemption/');
    cy.get('#id_exe_radio_1').check();
    cy.get('#id_submit').click();
    cy.get('#id_file').click();
    cy.get('#id_submit').click();
    cy.get('.govuk-button').click();
    /* ==== End Cypress Studio ==== */
  });

  /* ==== Test Created with Cypress Studio ==== */
  it('exemption_fail', function() {
    /* ==== Generated with Cypress Studio ==== */
    cy.visit('exemption/');
    cy.get('#id_exe_radio_2').check();
    cy.get('#id_submit').click();
    /* ==== End Cypress Studio ==== */
  });
})
  
import './base.cy'

describe('session timeout tests', () => {

  beforeEach(()=>{
    cy.clock();
    cy.start()
  });

  it('session_timeout_dialog_success', () => {

    cy.get('.govuk-grid-column-two-thirds > .govuk-button').click();
    cy.get('#id_registrar_organisation').clear().type('WeRegister')
    cy.get('#id_registrar_name').clear('Test');
    cy.get('#id_registrar_phone').clear('01225672345');
    cy.get('#id_registrar_email').clear('test@example.gov.uk');
    cy.get('#id_submit').click();

    // check if model_dialog doesn't exist
    cy.get('#modal_dialog').should('not.be.visible');
    // clock tick
    cy.tick(15 * 60 * 1000);
    cy.get('#modal_dialog').should('exist');
    cy.get('#modal_dialog').should('be.visible');

  });

  it('session_timeout_click_continue_session', () => {

    cy.get('.govuk-grid-column-two-thirds > .govuk-button').click();
    cy.get('#id_registrar_organisation').clear().type('WeRegister')
    cy.get('#id_registrar_name').clear('Test');
    cy.get('#id_registrar_phone').clear('01225672345');
    cy.get('#id_registrar_email').clear('test@example.gov.uk');
    cy.get('#id_submit').click();

    // clock tick
    cy.tick(15 * 60 * 1000);
    cy.get('#modal_dialog').should('exist');
    cy.get('#modal_dialog').should('be.visible');

    // Click the "Continue" button
    cy.get('#session-continue').click();

    // Check if the warning modal is hidden
    cy.get('#modal_dialog').should('not.be.visible');

  });

  it('session_timeout_session_ended', () => {
    cy.get('.govuk-grid-column-two-thirds > .govuk-button').click();
    cy.get('#id_registrar_organisation').clear().type('WeRegister')
    cy.get('#id_registrar_name').clear().type('Test');
    cy.get('#id_registrar_phone').clear().type('01225672345');
    cy.get('#id_registrar_email').clear().type('test@example.gov.uk');
    cy.get('#id_submit').click();

    // Simulate 15 minutes of inactivity
    cy.tick(15 * 60 * 1000);

    // Ensure the modal dialog exists and is visible
    cy.get('#modal_dialog').should('exist');
    cy.get('#modal_dialog').should('be.visible');

    // Simulate additional 5 minutes of inactivity
    cy.tick(5 * 60 * 1000);

    // Check if the warning modal is still hidden
    cy.get('#modal_dialog').should('not.be.visible');

    // Check if the user is not redirected to the session-ended page
    cy.url().should('include', '/session-ended/');
  });
})

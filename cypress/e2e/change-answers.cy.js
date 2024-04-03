import './base.cy'

describe('Changing answers at the end of the process', () => {
  it('lets you change registrants details', () => {
    cy.goToConfirmation()
    cy.get("a[href='/change-registrar-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrar details')

    // check previously entered registrar details are pre-filled
    cy.get('#id_registrar_organisation').should('have.value', 'WeRegister')
    cy.get('#id_registrar_name').should('have.value', 'Joe Bloggs')
    cy.get('#id_registrar_phone').should('have.value', '01225672345')
    cy.get('#id_registrar_email').should('have.value', 'joe@example.org')

    // change a value
    cy.get('#id_registrar_phone').clear().type('01225672345')

    // go back to answers
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(1, '01225672345')
  })
})

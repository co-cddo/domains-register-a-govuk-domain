import './base.cy'

describe('Accessible autocomplete', () => {
  it('pops up when user types', () => {
    cy.goToRegistrarDetails()
    cy.get('#id_registrar_organisation').clear().type('WeRegister')

    cy.get('#id_registrar_organisation__listbox').should('be.visible')
    cy.get('.autocomplete__option').should('include.text', 'WeRegister')
  })
})

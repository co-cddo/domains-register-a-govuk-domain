import './base.cy'

describe('Registrant not eligible', () => {
  it('Says registrant is not eligible if user selects other type of organisation', () => {
    cy.goToRegistrantType()
    cy.chooseRegistrantType(12)
    cy.checkPageTitleIncludes('Your registrant is not eligible for a .gov.uk domain name')
  })
})

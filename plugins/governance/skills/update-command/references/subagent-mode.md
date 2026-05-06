# Step 2B: Subagent Mode (fallback)

This reference is consulted when Step 1 (Mode Selection) does NOT detect Agent Teams in the session context. Otherwise use Team Mode (`references/team-mode.md`).

When Agent Teams are not available, execute the existing workflow:

## Planning

1. **Skill Compliance**
   - MUST follow skills identified in Phase 1
   - If no skill exists, follow project conventions
   - Reference specific skill files when applicable

2. **Primary Implementation**
   - Apply specific area changes from parsed arguments
   - Add missing sections from template
   - Update targeted sections per change requests
   - Reorganize content to match structure
   - Migrate existing content appropriately
   - Update the content such that the changes are clearly reflected

3. **Standards Enforcement**
   - Apply standards from `[plugin]/constitution/standards/`
   - Follow template structure
   - No instruction comments copied from the template
   - Ensure targeted changes align with standards

4. **Edge Case Handling**
   - Preserve custom useful content
   - Handle missing sections gracefully
   - Maintain backward compatibility

## Verification

1. **Quality Assurance**
   - Verify NO comments remain
   - Check markdown formatting and structure
   - Validate frontmatter syntax and completeness
   - Verify all requested changes implemented

2. **Side Effect Validation**
   - Core functionality preserved
   - Custom content maintained
   - Template compliance achieved
